from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_file,
    send_from_directory
)

import os
import threading
import time
import datetime
import subprocess

from domains.webapp.fileprocessing import FileManager
from domains.webapp.execution import ScriptExecutor

app = Flask(__name__)

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/linuxaio/digest/')
SCRIPT_PATH = 'linuxaioperf.py'
unique_id = None


def log_message(message, log_level='Info'):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time}: [{log_level}] [app.py] {message}")


log_message("Starting Linux AiO app.py")


@app.route('/')
def index():
    return render_template('upload.html')


# create_unique_dir function moved to domains.webapp.fileprocessing.FileManager


def delete_contents():
    find_command = (
        f"find {UPLOAD_FOLDER} -mindepth 1 "
        f"-maxdepth 1 -type d -mmin +10"
    )

    find_process = subprocess.Popen(
        find_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = find_process.communicate()

    if find_process.returncode == 0:
        dirs_to_delete = stdout.decode().split('\n')[:-1]
        for dir_to_delete in dirs_to_delete:
            try:
                subprocess.run(["rm", "-rf", dir_to_delete])
                log_message("Deleted directory: " + dir_to_delete)
            except Exception as e:
                error_message = (
                    "Failed to delete directory: " + dir_to_delete +
                    " Error: " + str(e)
                )
                log_message(error_message)


def delete_contents_periodically(interval_seconds):
    log_message("Deleting contents periodically")
    while True:
        log_message("Deleting contents periodically")
        time.sleep(interval_seconds)
        delete_contents()


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # Initialize domain services
            file_manager = FileManager()
            script_executor = ScriptExecutor()

            # Process the uploaded file
            try:
                unique_id, unique_dir = file_manager.process_upload(
                    uploaded_file,
                    UPLOAD_FOLDER,
                    os.path.dirname(__file__)
                )
                log_message(
                    f"File processed successfully. Report ID: {unique_id}")
            except Exception as e:
                log_message(f"File processing failed: {e}", "Error")
                return render_template('bad_gzip_file.html'), 400

            # Execute the performance analysis script
            log_message("Executing performance analysis script")
            exit_code = script_executor.execute_linuxaioperf(unique_dir)

            if exit_code != 0:
                log_message(
                    f"Script execution failed with exit code: {exit_code}",
                    "Error")
                return render_template('generic_error.html',
                                       reportid=unique_id), 500

            # Construct the URL for the report page
            log_message("Constructing report URL")
            report_url = url_for('view_report', dir=unique_dir, _external=True)
            log_message(f"Report ID: {unique_id}")

            # Redirect the user to the report page
            return redirect(report_url)

        return 'No file uploaded.'

    except Exception as e:
        log_message(f"Error: {e}", "Error")
        reportid = (unique_dir.split("/")[-1] if 'unique_dir' in locals()
                    else "unknown")
        return render_template('generic_error.html', reportid=reportid), 500


@app.route('/get_text', methods=['GET'])
def get_text():
    try:
        file_name = request.args.get('file_name', default='file.txt', type=str)
        return send_from_directory('./manpages',
                                   file_name,
                                   as_attachment=False)
    except FileNotFoundError:
        return 'File not found', 404


@app.route('/view_report')
def view_report():
    try:
        unique_dir = request.args.get('dir')
        report_path = os.path.join(unique_dir, 'linuxaioperf_report.html')
        return send_file(report_path)
    except Exception as e:
        reportid = unique_dir.split("/")[-1]
        log_message(f"Error: {e}", "Error")
        return render_template('generic_error.html',
                               reportid=reportid), 500


def start_delete_thread():
    log_message("Starting delete thread")
    delete_thread = threading.Thread(
        target=delete_contents_periodically, args=(600,))
    delete_thread.daemon = True
    delete_thread.start()


start_delete_thread()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
