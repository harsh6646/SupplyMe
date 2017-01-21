from flask import render_template, flash, redirect, session, url_for
from flask import request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, EditForm, LendItem, BorrowItem
from .models import User, Lend, Borrow, Pending
from datetime import datetime
from .oauth import OAuthSignIn


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    lend_items = Lend.query.all()
    borrow_items = Borrow.query.all()
    pending_items = Pending.query.all()
    return render_template('index.html', user=user,
                           litems=lend_items, bitems=borrow_items,
                           pitems=pending_items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', title="Sign in",
                           form=form)


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, profile_picture = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email,
                    profile_picture=profile_picture)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


def after_login(resp):
    if ((resp.email is None) or (resp.email == '')):
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()

    if (user is None):
        nickname = resp.nickname
        if ((nickname is None) or (nickname == '')):
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False

    if ('remember_me' in session):
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.before_request
def before_request():
    g.user = current_user
    if (g.user.is_authenticated):
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if (user is None):
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    return render_template('user.html', user=user)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if (form.validate_on_submit()):
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        g.user.location = form.location.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        form.location.data = g.user.location
    return render_template('edit.html', form=form)


@app.route('/lend_item', methods=['GET', 'POST'])
def lend_item():
    form = LendItem()
    if (form.validate_on_submit()):
        lend = Lend(item_name=form.item_name.data,
                    item_location=form.item_location.data,
                    item_time_pickup=form.item_time_pickup.data,
                    lister=g.user, item_status=0)
        db.session.add(lend)
        db.session.commit()
        flash('Your item is now live!')
        return redirect(url_for('index'))
    return render_template('lend_item.html', form=form)


@app.route('/borrow_item', methods=['GET', 'POST'])
def borrow_item():
    form = BorrowItem()
    if (form.validate_on_submit()):
        borrow = Borrow(item_name=form.item_name.data,
                        item_location=form.item_location.data,
                        item_time_pickup=form.item_time_pickup.data,
                        lister=g.user, item_status=0)
        db.session.add(borrow)
        db.session.commit()
        flash('Your item is now live!')
        return redirect(url_for('index'))
    return render_template('borrow_item.html', form=form)


@app.route('/lend/<int:id>', methods=['GET', 'POST'])
def lend_click(id):
    # get the item to lend
    lend_item = Lend.query.get(id)
    lender_id = lend_item.user_id
    lender = User.query.get(lender_id)
    pending_item = Pending(item_name=lend_item.item_name,
                           item_location=lend_item.item_location,
                           item_time_pickup=lend_item.item_time_pickup,
                           user_click_name=g.user.nickname,
                           user_lister_name=lender.nickname,
                           lister=g.user)
    db.session.add(pending_item)
    db.session.delete(lend_item)
    db.session.commit()
    flash('The item is now pending transaction!')
    return redirect(url_for('index'))


def borrow_click():
    # get the item that someone wants to borrow
    borrow_item = Borrow.query.get(id)
    lender_id = borrow_item.user_id
    lender = User.query.get(lender_id)
    pending_item = Pending(item_name=borrow_item.item_name,
                           item_location=borrow_item.item_location,
                           item_time_pickup=borrow_item.item_time_pickup,
                           user_click_name=g.user.nickname,
                           user_lister_name=lender.nickname,
                           lister=g.user)
    db.session.add(pending_item)
    db.session.delete(borrow_item)
    db.session.commit()
    flash('The item is now pending transaction!')
    return redirect(url_for('index'))


@app.route('/pending/<int:id>', methods=['GET', 'POST'])
def pending(id):
    pending = Pending.query.get(id)
    db.session.delete(pending)
    db.session.commit()
    flash('The transaction was successful')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
