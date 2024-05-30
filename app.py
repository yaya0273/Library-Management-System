from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date,timedelta

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/yayar/Desktop/Documents/IITM/MAD I Project/Project/Code/database.sqlite3"
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Book(db.Model):
    __tablename__='book'
    ID=db.Column(db.Integer,primary_key=True, autoincrement=True)
    Name=db.Column(db.String)
    Author=db.Column(db.String)
    SID=db.Column(db.Integer, db.ForeignKey("section.ID"))

class Section(db.Model):
    __tablename__='section'
    ID=db.Column(db.Integer,primary_key=True, autoincrement=True)
    Name=db.Column(db.String)
    Desc=db.Column(db.String)

class Users(db.Model):
    __tablename__='users'
    ID=db.Column(db.Integer,primary_key=True)
    Password=db.Column(db.String)

class Issued(db.Model):
    __tablename__='issued'
    SL=db.Column(db.Integer,autoincrement=True,primary_key=True)
    BID=db.Column(db.Integer)
    UID=db.Column(db.Integer)
    Status=db.Column(db.String)
    DOI=db.Column(db.String)
    DOR=db.Column(db.String)


@app.route('/',methods=["GET","POST"])
def login():
    if(request.method=="GET"):
        return render_template("Login.html")
    else:
        id=request.form["id"]
        password=request.form["password"]
        data=Users.query.filter_by(ID=id).first()
        if(data.Password==password):
            if(id=='admin'):
                return redirect("/admin")
            return redirect("/user/"+str(id))
        
@app.route('/register',methods=["GET","POST"])
def register():
    if(request.method=="GET"):
        return render_template("Register.html")
    else:
        id=request.form["id"]
        p1=request.form["p1"]
        p2=request.form["p2"]
        n=Users.query.filter_by(ID=id).count()
        if(n!=0):
            return render_template("User_Exists.html")
        elif(p1!=p2):
            return render_template("Passwords_Match.html")
        else:
            data=Users(ID=id,Password=p1)
            db.session.add(data)
            db.session.commit()
            return redirect("/user/"+id)
        
@app.route('/user/<id>',methods=["GET","POST"])
def user(id):
    if(request.method=="GET"):
        data=Issued.query.filter_by(Status="Current").filter(Issued.DOR<date.today()).all()
        #data=Issued.query.filter_by(Status="Current").all()
        for i in data:
            '''rdate=date(int(i.DOR[:4]),int(i.DOR[5:7]),int(i.DOR[9:11]))
            print(rdate>date.today())'''
            return_book(i.BID,i.UID)
        books=Issued.query.filter_by(UID=id).all()
    else:
        p=request.form["p"]
        books=Issued.query.join(Book, Issued.BID==Book.ID).join(Section, Section.ID==Book.SID).filter(Issued.UID==id).filter(or_(Book.Name.like(f"%{p}%"),Book.Author.like(f"%{p}%"),Section.Name.like(f"%{p}%"))).all()
    current=[]
    completed=[]
    requested=[]
    for i in books:
        if(i.Status=="Current"):
            current.append(i.BID)
        elif(i.Status=="Completed"):
            completed.append(i.BID)
        else:
            requested.append(i.BID)
    bcu=db.session.query(Book,Issued,Section).filter(Book.ID==Issued.BID).filter(Book.SID==Section.ID).filter(Issued.UID==id).filter(Book.ID.in_(current)).all()
    bco=Book.query.filter(Book.ID.in_(completed)).all()
    bre=Book.query.filter(Book.ID.in_(requested)).all()
    for i in bco+bre:
        i.SID=Section.query.filter_by(ID=i.SID).first().Name
    return render_template("My_Books.html",bcu=bcu,bco=bco,bre=bre, id=id)

@app.route('/return/<bid>/<uid>',methods=["GET","POST"])
def return_book(bid,uid):
    data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
    data.Status="Completed"
    db.session.commit()
    return redirect("/user/"+data.UID)

@app.route('/request/<bid>/<uid>',methods=["GET","POST"])
def request_book(bid,uid):
    n=Issued.query.filter_by(UID=uid).filter(Issued.Status.in_(['Current', 'Requested'])).count()
    if(n>=5):
        return render_template("Limit.html",id=uid)
    else:
        try:
            data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
            data.Status="Requested"
        except:
            data=Issued(BID=bid,UID=uid,Status="Requested")
            db.session.add(data)
        db.session.commit()
        return redirect("/user/"+uid)

@app.route('/cancel/<bid>/<uid>',methods=["GET","POST"])
def cancel_book(bid,uid):
    data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
    db.session.delete(data)
    db.session.commit()
    return redirect("/user/"+uid)

@app.route('/<id>/books',methods=["GET","POST"])
def books(id):
        if(request.method=="GET"):
            books=Book.query.all()
        else:
            p=request.form["p"]
            books=Book.query.join(Section,Section.ID==Book.SID).filter(or_(Book.Name.like(f"%{p}%"),Book.Author.like(f"%{p}%"),Section.Name.like(f"%{p}%"))).all()
        for i in books:
            i.SID=Section.query.filter_by(ID=i.SID).first().Name
        return render_template("Books.html",books=books,id=id)

@app.route('/admin',methods=["GET","POST"])
def admin():
    if(request.method=="GET"):
        data=Section.query.all()
    else:
        p=request.form["p"]
        data=Section.query.filter(Section.Name.like(f"%{p}%")).all()
    return render_template("L_Dash.html",sections=data)

@app.route('/admin/add/<id>',methods=["GET","POST"])
def add_book(id):
    if(request.method=="GET"):
        data=Section.query.filter_by(ID=id).first()
        return render_template("Add_Book.html",section=data)
    else:
        title=request.form["title"]
        author=request.form["author"]
        data=Book(Name=title,Author=author,SID=id)
        db.session.add(data)
        db.session.commit()
        return redirect("/admin")

@app.route('/admin/view/<id>',methods=["GET","POST"])
def view(id):
    books=Book.query.filter_by(SID=id).all()
    sect=Section.query.filter_by(ID=id).first().Name
    return render_template("View_Section.html",books=books,Section=sect)

@app.route('/admin/requests',methods=["GET","POST"])
def requests():
    if(request.method=="GET"):
        data=Issued.query.filter_by(Status="Requested")
    else:
        p=request.form["p"]
        data=Issued.query.join(Book, Book.ID==Issued.BID).filter(Issued.Status=="Requested").filter(or_(Issued.UID.like(f"%{p}%"),Book.Name.like(f"%{p}%"))).order_by("UID").all()
    for i in data:
        i.BID=Book.query.filter_by(ID=i.BID).first().Name
    return render_template("Requests.html",data=data)

@app.route('/admin/accept/<bid>/<uid>',methods=["GET","POST"])
def accept(bid,uid):
    bid=Book.query.filter_by(Name=bid).first().ID
    data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
    data.Status="Current"
    data.DOI=date.today()
    data.DOR=date.today()+timedelta(days=7)
    db.session.commit()
    return redirect("/admin/requests")

@app.route('/admin/decline/<bid>/<uid>',methods=["GET","POST"])
def decline(bid,uid):
    bid=Book.query.filter_by(Name=bid).first().ID
    data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin/requests")

@app.route('/admin/issued',methods=["GET","POST"])
def issued():
    if(request.method=="GET"):
        data=Issued.query.filter_by(Status="Current").order_by("UID").all()
    else:
        p=request.form["p"]
        data=Issued.query.join(Book, Book.ID==Issued.BID).filter(Issued.Status=="Current").filter(or_(Issued.UID.like(f"%{p}%"),Book.Name.like(f"%{p}%"))).order_by("UID").all()
    for i in data:
            i.BID=Book.query.filter_by(ID=i.BID).first().Name
    return render_template("Issued.html",issued=data)

@app.route('/admin/revoke/<uid>/<bid>',methods=["GET","POST"])
def revoke(uid,bid):
    bid=Book.query.filter_by(Name=bid).first().ID
    data=db.session.query(Issued).filter_by(BID=bid).filter_by(UID=uid).first()
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin/issued")

@app.route('/admin/adds',methods=["GET","POST"])
def add_section():
    if(request.method=="GET"):
        return render_template("Add_Section.html")
    else:
        name=request.form["name"]
        desc=request.form["desc"]
        data=Section(Name=name,Desc=desc)
        db.session.add(data)
        db.session.commit()
        return redirect("/admin")
    
@app.route('/admin/editb/<id>',methods=["GET","POST"])
def edit_book(id):
    if(request.method=="GET"):
        book=Book.query.filter_by(ID=id).first()
        sections=Section.query.all()
        return render_template("Edit_Book.html",book=book,sections=sections)
    else:
        title=request.form["title"]
        author=request.form["author"]
        section=request.form["section"]
        data=db.session.query(Book).filter_by(ID=id).first()
        data.Name=title
        data.Author=author
        data.SID=section
        db.session.commit()
        return redirect("/admin/view/"+section)
    
@app.route('/admin/deleteb/<id>',methods=["GET","POST"])
def delete_book(id):
    data=db.session.query(Book).filter_by(ID=id).first()
    sid=data.SID
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin/view/"+str(sid))

@app.route('/admin/edits/<id>',methods=["GET","POST"])
def edit_section(id):
    if(request.method=="GET"):
        section=Section.query.filter_by(ID=id).first()
        return render_template("Edit_Section.html",section=section)
    else:
        name=request.form["name"]
        desc=request.form["desc"]
        data=db.session.query(Section).filter_by(ID=id).first()
        data.Name=name
        data.Desc=desc
        db.session.commit()
        return redirect("/admin")
    
@app.route('/admin/deletes/<id>',methods=["GET","POST"])
def delete_section(id):
    data=db.session.query(Section).filter_by(ID=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin")

if __name__=='__main__':
    app.run()