import base64
import os
from io import BytesIO

from dotenv import load_dotenv
from secrets import token_hex
from flask import (Flask, Response, flash, redirect, render_template, request,
                   session, url_for)
from flask_bootstrap import Bootstrap
from PIL import Image

from filters import datetimeformat, file_type
from resources import (_get_s3_client, get_bucket, get_buckets_list,
                       get_presigned_url, _get_s3_resource)

load_dotenv('.env')


app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
Bootstrap(app)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)


@app.route('/files')
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()
    image_urls = list()

    s3 = _get_s3_client()
    for summary in summaries:
        image_urls.append(get_presigned_url(s3, summary.key))

    return render_template('files.html', my_bucket=my_bucket, files=zip(summaries, image_urls))


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    max_size = 640, 480

    in_mem_file = BytesIO()

    img = Image.open(file)
    img.thumbnail(max_size, Image.ANTIALIAS)
    img.save(in_mem_file, format=img.format)

    my_bucket = get_bucket()
    my_bucket.Object("folder/"+file.filename).put(Body=in_mem_file.getvalue())

    flash('File uploaded successfully')
    return redirect(url_for('files'))


@app.route('/upload_b64', methods=["GET", "POST"])
def upload_b64():
    if request.method == "POST":
        try:
            img = base64.b64decode(request.form['img_string'])
            buf = BytesIO(img)
        except Exception as err:
            print("[ERROR]: " + str(err))
            return redirect(url_for('upload_b64'))

        s3 = _get_s3_resource()
        my_bucket = s3.Bucket("azsxcx")
        image_path = f"images/" + token_hex(8) + ".jpg"
        my_bucket.Object(image_path).put(Body=buf.getvalue())    # noqa
        return redirect(url_for('index'))

    return render_template('upload_b64.html')


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )


if __name__ == "__main__":
    app.run(debug=True)
