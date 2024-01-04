from flask import Blueprint,render_template,request,url_for, g,flash
from werkzeug.utils import redirect

from pybo.models import Question, Answer, User , answer_voter
from pybo.forms import QuestionForm,AnswerForm
from pybo.views.auth_views import login_required
from .. import db

from datetime import datetime
from sqlalchemy import func


bp=Blueprint('question',__name__,url_prefix='/question')

@bp.route('/list/')
def _list():
    page = request.args.get('page',type=int,default=1) #페이지
    kw = request.args.get("kw",type=str,default='')

    question_list = Question.query.order_by(Question.create_date.desc())
    print(type(question_list))
    if kw:
        search = "%%{}%%".format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username)\
        .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    question_list = question_list.paginate(page=page,per_page=10)
    print((type(question_list)))
    return render_template('question/question_list.html', question_list=question_list,page=page,kw=kw)
#get 메소드로 파라미터를 전달 받는 방법
@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    page = request.args.get("page",type=int,default=1) #답변 페이징
    sort = request.args.get("sort",type=str,default="best") # 답변 정렬
    print(sort)

    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    answer_list = ""
    if question.answer_set and sort == "new": # 최신순
        answer_list = Answer.query.filter(Answer.question_id == question_id).order_by(Answer.create_date.desc())
        answer_list = answer_list.paginate(page=page,per_page=10)

    if question.answer_set and sort == "best":
        print("bestifstate")
        #sub_query = db.session.query(answer_voter.c.answer_id, func.count().label("voter_count")).group_by(answer_voter.c.answer_id).subquery()
        #answer_list = db.session.execute(select([Answer,sub_query.c.voter_count]).outerjoin(sub_query,Answer.id == sub_query.c.answer.id).filter(Answer.question.id == question_id).order_by(sub_query.c.voter_count.desc()))
        subquery = db.session.query(
            answer_voter.c.answer_id,
            func.count().label('voter_count')
        ).group_by(answer_voter.c.answer_id).subquery()

        answer_list = db.session.query(Answer).outerjoin(
    subquery, Answer.id == subquery.c.answer_id
).filter(Answer.question_id == question_id).order_by(subquery.c.voter_count.desc())




        answer_list = answer_list.paginate(page=page, per_page=10)
        print(answer_list.items[0])




# 아래 방법은 폐기함
#    #추천수 정렬
#    if question.answer_set and sort == "best":
#        question.answer_set = sorted(question.answer_set, key=lambda x: len(x.voter),reverse=True)
#
#    #최신순 정렬
#    if question.answer_set and sort == "new":
#        question.answer_set = sorted(question.answer_set, key=lambda x: x.create_date, reverse=True)

    return render_template('question/question_detail.html',page=page,sort=sort,question=question, form=form,answer_list=answer_list)

@bp.route('/create',methods=('GET','POST'))
@login_required
def create():
    form = QuestionForm()


    # POST 메소드이고 폼의 유효성검사가 타당하면
    if request.method=='POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data,content=form.content.data,create_date=datetime.now(), user=g.user)

        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))



    return render_template('question/question_form.html',form=form)

@bp.route("/modify/<int:question_id>", methods=("GET", "POST"))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash("수정할 권한이 없습니다.")
        return redirect(url_for("question.detail",question_id=question_id))

    if request.method == "POST":
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date=datetime.now()
            db.session.commit()
            return redirect(url_for("question.detail",question_id=question_id))
    else:
        form = QuestionForm(obj=question)

    return render_template("question/question_form.html", form=form)


@bp.route("/delete/<int:question_id>")
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash("삭제할 권한이 없습니다.")
        return redirect(url_for("question.detail",question_id=question_id))

    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("question._list"))


@bp.route("/vote/<int:question_id>")
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)

    if g.user == _question.user:
        flash("본인이 작성한 글은 추천할 수 없습니다.")
    else:
        _question.voter.append(g.user)
        db.session.commit()

    return redirect(url_for("question.detail", question_id=question_id))