import os
import stat
import time
import subprocess

from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

EVALB_EXEC = './evalb'

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['gld', 'tst', 'txt'])

st = os.stat(EVALB_EXEC)
os.chmod(EVALB_EXEC, st.st_mode | stat.S_IEXEC)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timestamp = str(time.time)
        gold_file = request.files['gold-file']
        test_file = request.files['test-file']

        if not (gold_file and test_file):
            return 'Failed to upload files. Try again!'

        # if not (allowed_file(gold_file.filename) and
        #        allowed_file(test_file.filename)):
        #    return 'Uploaded file should be with [{}] extensions'.format(
        #        ', '.join(ALLOWED_EXTENSIONS))

        gold_filename = timestamp + '-gold-' + \
            secure_filename(gold_file.filename)
        test_filename = timestamp + '-test-' + \
            secure_filename(test_file.filename)

        gold_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                 gold_filename)
        test_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                 test_filename)

        gold_file.save(gold_path)
        test_file.save(test_path)

        result = subprocess.run([EVALB_EXEC, gold_path, test_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        output = result.stdout.decode('utf8')

        return '<pre>{}</pre>'.format(output)  # redirect(url_for('index'))

    return """
    <!doctype html>
    <title>Evalb</title>
    <h1>Evalb</h1>
    <h5>Notes from the assignment notebook on EVALB: Some pre- or postprocessing may be necessary on the trees to compare them.
    Note in particular that some trees contain an additional ROOT or TOP node which should not be part of the evaluation.
    In general, the format of the gold and test files should match.</h5>
    <h6>You can check some working samples files from the <a href="http://nlp.cs.nyu.edu/evalb/">Evalb</a> website. It is in the last version of the downloadable archive file.</h6>
    <form action="" method=post enctype=multipart/form-data>
      <p>Gold file: <input type=file name=gold-file></p>
      <p>Test file: <input type=file name=test-file></p>
      <p><input type=submit value=Run></p>
    </form>"""
    #<p>%s</p>
    #""" % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
