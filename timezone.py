from flask import Flask, render_template_string, request
from datetime import datetime
import pytz

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang="en">

<head>
    <title>World Clock</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            background-color: #F7F8FC;
            align: center;
            color: #000000;
            font-family: Arial, sans-serif;
            padding-top: 60px;
        }

        h1 {
            font-size: 2.5em;
        }

        .container {
            text-align: center;
            align: center;
            background-color: #fff;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            width: 800px;
            padding: 20px;
        }

        #amsterdamTime {
            font-size: 1.2em;
            width: 700px;
        }

        #selectedTimezone {
            width: 700px;
            font-size: 1.2em;
        }
        .search-input {
            margin: 10px 0;
            padding: 10px;
            width: 700px;
            background-color: #F7F8FC;
        }
        .form-group {
            width: 800px;
            padding: 10px;
        }

        .form-control {
            width: 700px;
            padding: 10px;
            display: inline-block;
            margin-bottom: 10px;
        }
    </style>
</head>

<body>
    <div class="container" align="center">
        <h1>World Clock</h1>

        <div class="row" align="center">
            <div align="center">
                <p id="amsterdamTime"></p>

                <div class="form-group">
                    <input type="text" class="form-control search-input" id="timezoneSearch" oninput="filterTimezones()" placeholder="Search Timezone">
                    <select class="form-control" id="timezoneSelect" onchange="updateTime()">
                        {% for timezone, offset in timezones_with_offset %}
                        <option value="{{ timezone }}" {% if timezone == selected_timezone %}selected{% endif %}>
                            {{ timezone }} (UTC {{ offset }})
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <p id="selectedTimezone"></p>
            </div>
        </div>
    </div>

    <script>
        function filterTimezones() {
            const searchInput = document.getElementById("timezoneSearch");
            const filter = searchInput.value.toUpperCase();
            const select = document.getElementById("timezoneSelect");
            const options = select.options;

            for (let i = 0; i < options.length; i++) {
                const optionText = options[i].text.toUpperCase();
                const optionValue = options[i].value.toUpperCase();
                const isMatch = optionText.includes(filter) || optionValue.includes(filter);

                options[i].style.display = isMatch ? "block" : "none";

                if (isMatch && select.value !== options[i].value) {
                    select.value = options[i].value;
                    updateTime();
                }
            }
        }

        function updateTime() {
            const selectedTimezone = document.getElementById("timezoneSelect").value;

            fetch('/update_time', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'timezoneSelect': selectedTimezone,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("amsterdamTime").textContent = `Amsterdam Time: ${data.amsterdam_time}`;
                    document.getElementById("selectedTimezone").textContent = data.selected_time;

                    const url = new URL(window.location.href);
                    url.searchParams.set('timezone', selectedTimezone);
                    history.replaceState(null, null, url.toString());
                });
        }

        setInterval(updateTime, 1000);
        updateTime();
    </script>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.10.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>

</html>

"""

@app.route('/')
def index():
    selected_timezone = request.args.get('timezone', 'Europe/Amsterdam')
    timezones_with_offset = [(timezone, get_utc_offset(timezone)) for timezone in pytz.all_timezones]
    return render_template_string(html_template, timezones_with_offset=timezones_with_offset, selected_timezone=selected_timezone)

@app.route('/update_time', methods=['POST'])
def update_time():
    selected_timezone = request.form.get('timezoneSelect')
    
    amsterdam_time = get_formatted_time("Europe/Amsterdam")
    selected_time = get_formatted_time(selected_timezone)

    return {'amsterdam_time': amsterdam_time, 'selected_time': f"{selected_timezone} Time: {selected_time}"}

def get_formatted_time(timezone):
    current_time = datetime.now(pytz.timezone(timezone))
    return current_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def get_utc_offset(timezone):
    offset = datetime.now(pytz.timezone(timezone)).strftime('%z')
    return f"{offset[:-2]}:{offset[-2:]}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
