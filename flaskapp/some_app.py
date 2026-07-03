from flask import Flask, render_template

# 1. ОБЯЗАТЕЛЬНО: Создаем объект приложения Flask
app = Flask(__name__)

# Наша новая функция сайта
@app.route("/data_to")
def data_to():
    # Создаем переменные с данными для передачи в шаблон
    some_pars = {'user': 'Ivan', 'color': 'red'} 
    some_str = 'Hello my dear friends!'
    some_value = 10
    
    # Передаем данные в шаблон и вызываем его
    return render_template(
        'simple.html', 
        some_str=some_str,
        some_value=some_value, 
        some_pars=some_pars
    )

# 2. ОБЯЗАТЕЛЬНО: Добавляем блок для локального запуска сервера
if __name__ == "__main__":
    app.run(debug=True)
