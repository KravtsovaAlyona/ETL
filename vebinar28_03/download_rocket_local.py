import json
import pathlib
import requests
import requests.exceptions as requests_exceptions
import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import requests

TELEGRAM_BOT_TOKEN = "7491834096:AAGWYR3Bwr1Pq0fTFwenQzp4XaOabgaWRcc"  # Замени на реальный токен
TELEGRAM_CHAT_ID = "1482158775"  # Замени на реальный chat_id

def send_telegram_alert(context):
    """Функция отправки сообщений в Telegram при ошибке DAG."""
    message = f"❌ Ошибка в DAG {context['task_instance'].dag_id}\nTask: {context['task_instance'].task_id}\nError: {context['exception']}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
dag = DAG(
    dag_id="download_rocket_local",
    description="Download rocket pictures of recently launched rockets.",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval="@daily",
)

download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /opt/airflow/data/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",
    dag=dag,
)

def _get_pictures():
    images_dir = "/opt/airflow/data/images"
    pathlib.Path(images_dir).mkdir(parents=True, exist_ok=True)

    with open("/opt/airflow/data/launches.json") as f:
        launches = json.load(f)
        image_urls = [launch["image"] for launch in launches["results"]]
        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                response.raise_for_status()  # Проверка на HTTP-ошибки (404, 500 и т. д.)
                
                image_filename = image_url.split("/")[-1]
                target_file = f"{images_dir}/{image_filename}"
                with open(target_file, "wb") as f:
                    f.write(response.content)
                
                print(f"Downloaded {image_url} to {target_file}")
            
            except (requests_exceptions.MissingSchema, requests_exceptions.ConnectionError, requests_exceptions.HTTPError) as e:
                error_message = f"Ошибка загрузки {image_url}: {e}"
                print(error_message)
                send_telegram_message(error_message)  # 🔹 Отправка ошибки в Telegram

get_pictures = PythonOperator(
    task_id="get_pictures",
    python_callable=_get_pictures,
    on_failure_callback=send_telegram_alert,
    dag=dag,
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /opt/airflow/data/images/ | wc -l) images."',
    dag=dag,
)

download_launches >> get_pictures >> notify