#encoding:utf-8

#输入python模块以及unpickle的代码部分
from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
import pickle,sqlite3,os
import numpy as np



#确定一些文件的位置信息
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir, 'pkl_objects/classifier.pkl'), 'rb'))
scl = pickle.load(open(os.path.join(cur_dir, 'pkl_objects/scaler.pkl'), 'rb'))
db = os.path.join(cur_dir, 'pd.sqlite')

#帮助函数
def convert(document):
	'''
	输入：字符串文本信息
	输出：转换成list格式的数字类型数组
	'''
	return [float(i) for i in document.strip().split(',')]

def classify(document):
	'''
	输入：字符串文本信息
	输出：（分类标签，标签对应的概率）
	'''
	data = np.array(convert(document))
	data = scl.transform(data)
	label = {0:'Type 1', 1:'Type 2', 2:'Type 3', 3:'Type 4', 4:'Type 5'}
	p1 = clf.predict_proba(data.reshape(1,-1))
	return label[np.argmax(p1)], np.max(p1)


def train(document, y):
	'''
	输入：（字符串文本信息，正确的标签）
	输出：无，对模型clf进行训练
	'''
	data = np.array(convert(document))
	data = scl.transform(data)
	clf.partial_fit(data, [y])


def sqlite_entry(path, document, y):
	'''
	输入：（数据库的path信息，字符串文本信息，正确的标签）
	输出：无，把数据写到数据库文件中去
	'''
	data = np.array(convert(document))
	conn = sqlite3.connect(path)
	c = conn.cursor()
	c.execute("INSERT INTO pd_data (pd_location, signal_width, rise_time, fall_time, peak_voltage,polarity, mean_voltage, rms, sd, skewness, kurtosis,crest, form_factor, MainFreq, phase_angle, T, W, pC,pd_class)"\
	    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", np.hstack([data,y]))
	conn.commit()
	conn.close()



#Flask主函数部分

app = Flask(__name__)

##定义index页面的表单
class ReviewForm(Form):
	pdreview = TextAreaField('',  [validators.DataRequired()])


@app.route('/')
def index():
	form = ReviewForm(request.form)
	return render_template('reviewform.html', form=form)


@app.route('/results', methods=['POST'])
def results():
	form = ReviewForm(request.form)
	if request.method == 'POST' and form.validate():
		review = request.form['pdreview']
		y, proba = classify(review)
		return render_template('results.html',  content=review,  prediction=y, probability=round(proba*100, 2))
	return render_template('reviewform.html', form=form)


@app.route('/thanks', methods=['POST'])
def feedback():
	feedback = request.form['feedback_button']
	review = request.form['review']
	prediction = request.form['prediction']

	inv_label = {'Type 1':1, 'Type 2':2, 'Type 3':3, 'Type 4':4, 'Type 5':5}
	y = inv_label[prediction]

	if feedback == '错误,应该是Type 1':
		y = 1
	elif feedback == '错误,应该是Type 2':
		y = 2
	elif feedback == '错误,应该是Type 3':
		y = 3
	elif feedback == '错误,应该是Type 4':
		y = 4
	elif feedback == '错误,应该是Type 5':
		y = 5

	train(review, y)
	sqlite_entry(db, review, y)

	return render_template('thanks.html')


if __name__ == '__main__':
	app.run(debug=True)