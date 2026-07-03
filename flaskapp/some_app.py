import os
import time
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from PIL import Image, ImageEnhance
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

app = Flask(__name__)

# === ВАША КОНФИГУРАЦИЯ ИЗ МЕТОДИЧКИ ===
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf3AkMtAAAAAAfmGtsO3d_0mSjXhYXY_exK0UmV'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf3AkMtAAAAAO3vuic4_-xwvwyYyMCTJLNvgXG_'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Форма для валидации капчи через Flask-WTF
class CaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()

def build_histogram(image_path, output_filename):
    """Построение графика распределения цветов RGB (Гистограмма)"""
    img = Image.open(image_path).convert('RGB')
    r, g, b = img.split()
    
    plt.figure(figsize=(6, 3))
    plt.plot(r.histogram(), color='red', label='Red', alpha=0.7)
    plt.plot(g.histogram(), color='green', label='Green', alpha=0.7)
    plt.plot(b.histogram(), color='blue', label='Blue', alpha=0.7)
    
    plt.title("Распределение цветов (RGB)")
    plt.xlabel("Интенсивность (0-255)")
    plt.ylabel("Количество пикселей")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    graph_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    plt.savefig(graph_path, bbox_inches='tight')
    plt.close()

@app.route("/", methods=["GET", "POST"])
def index():
    form = CaptchaForm()  # Создаем объект формы капчи
    error = None
    result_ready = False
    orig_img_url, res_img_url, orig_hist_url, res_hist_url = None, None, None, None
    
    if request.method == "POST":
        # Проверяем, нажал ли пользователь капчу Google
        if form.validate_on_submit():
            file = request.files.get("image_file")
            brightness_val = request.form.get("brightness")
            
            if not file or file.filename == '':
                error = "Пожалуйста, выберите файл изображения."
            elif not brightness_val:
                error = "Укажите уровень яркости."
            else:
                try:
                    # Сохраняем оригинал
                    orig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original.jpg')
                    file.save(orig_path)
                    
                    # Изменяем яркость (ползунок 0-200 переводим в коэффициент 0.0-2.0)
                    img = Image.open(orig_path)
                    enhancer = ImageEnhance.Brightness(img)
                    factor = float(brightness_val) / 100.0
                    res_img = enhancer.enhance(factor)
                    
                    res_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
                    res_img.save(res_path)
                    
                    # Генерируем графики
                    build_histogram(orig_path, 'orig_hist.png')
                    build_histogram(res_path, 'res_hist.png')
                    
                    # Пути с таймштампом против кэширования браузером
                    ts = int(time.time())
                    orig_img_url = f"/static/images/original.jpg?v={ts}"
                    res_img_url = f"/static/images/result.jpg?v={ts}"
                    orig_hist_url = f"/static/images/orig_hist.png?v={ts}"
                    res_hist_url = f"/static/images/res_hist.png?v={ts}"
                    
                    result_ready = True
                except Exception as e:
                    error = f"Ошибка при обработке изображения: {str(e)}"
        else:
            error = "Вы не прошли проверку Google reCAPTCHA! Подтвердите, что вы не робот. 🤖"
            
    return render_template(
        "index.html",
        form=form,
        error=error,
        result_ready=result_ready,
        orig_img_url=orig_img_url,
        res_img_url=res_img_url,
        orig_hist_url=orig_hist_url,
        res_hist_url=res_hist_url
    )

if __name__ == "__main__":
    app.run(debug=True)
