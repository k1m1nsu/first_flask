from flask import Blueprint , render_template, url_for
from werkzeug.utils import redirect

#from pybo.models import Question

bp = Blueprint('main',__name__,url_prefix='/')

@bp.route('/hello')
def hello_pybo():
    return "hello,pybo!"

@bp.route('/')
def index():
    #url_for(별칭.함수명) 등록된 블루프린트 별칭을 찾고 _list 함수명을 찾는다.
    #아래에서는 question alias 를 가진 블루프린트 객체의 함수 _list 에 리다이렉트 한다
    return redirect(url_for('question._list'))


'''
이 부분 question_views 로 옮김 

@bp.route('/')
def index():
    question_list = Question.query.order_by(Question.create_date.desc())


    return render_template('question/question_list.html',question_list=question_list)



@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html',question=question)

'''