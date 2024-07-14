import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, current_app, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import User, ShippingRate, AuthorizedPickUp, Prealert, Package, ActionRequired
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ProfileForm, UpdateRatesForm, AuthorizePickUpForm, PrealertForm, PackageForm
from functools import wraps
import uuid
from datetime import datetime, timezone


# Decorator to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Function to get uploaded files
def get_uploaded_files():
    rootdir = app.config['UPLOAD_FOLDER']
    file_lst = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            file_lst.append(file)
    return file_lst

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = ProfileForm(obj=user)
    
    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.phone = form.phone.data
            
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')

    return render_template('profile.html', form=form, user=user)


@app.route('/shipping_rates', methods=['GET'])
@login_required
def shipping_rates():
    form = UpdateRatesForm()
    rates = ShippingRate.query.all()

    for rate in rates:
        form.rates.append_entry({
            'pounds': rate.pounds,
            'usd': rate.usd,
            'jmd': rate.jmd,
        })

    return render_template('shipping_rates.html', form=form)

@app.route('/update_shipping_rates', methods=['POST'])
@login_required
@admin_required
def update_shipping_rates():
    form = UpdateRatesForm()
    if form.validate_on_submit():
        for rate_form in form.rates:
            rate = ShippingRate.query.filter_by(pounds=rate_form.pounds.data).first()
            if rate:
                rate.usd = rate_form.usd.data
                rate.jmd = rate_form.jmd.data
        db.session.commit()
        flash('Shipping rates updated successfully.', 'success')
        return redirect(url_for('shipping_rates'))
    return render_template('shipping_rates.html', form=form)

@app.route('/authorize-pickup', methods=['GET', 'POST'])
@login_required
def authorize_pickup():
    form = AuthorizePickUpForm()
    authorized_pickup_list = AuthorizedPickUp.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        if form.id.data:  # If ID is provided, we are editing an existing entry
            authorized_pickup = AuthorizedPickUp.query.get(form.id.data)
        else:  # Otherwise, we are adding a new entry
            authorized_pickup = AuthorizedPickUp(user_id=current_user.id)

        authorized_pickup.name = form.name.data
        authorized_pickup.telephone = form.telephone.data
        authorized_pickup.id_type = form.id_type.data
        authorized_pickup.id_number = form.id_number.data

        db.session.add(authorized_pickup)
        db.session.commit()
        flash('Authorized pick-up person has been updated.', 'success')
        return redirect(url_for('authorize_pickup'))

    return render_template('authorize_pickup.html', authorized_pickup_list=authorized_pickup_list, form=form)

@app.route('/admin-authorize-pickup')
@login_required
@admin_required
def admin_authorize_pickup():
    if current_user.role != 'admin':
        return redirect(url_for('authorize_pickup'))
    users = User.query.all()
    form = AuthorizePickUpForm()
    return render_template('admin_authorize_pickup.html', users=users, form=form)

@app.route('/add-edit-authorized-pickup', methods=['POST'])
@login_required
def add_edit_authorized_pickup():
    form = AuthorizePickUpForm()
    if form.validate_on_submit():
        if form.id.data:
            authorized_pickup = AuthorizedPickUp.query.get(form.id.data)
        else:
            authorized_pickup = AuthorizedPickUp(user_id=current_user.id)
        authorized_pickup.name = form.name.data
        authorized_pickup.telephone = form.telephone.data
        authorized_pickup.id_type = form.id_type.data
        authorized_pickup.id_number = form.id_number.data
        db.session.add(authorized_pickup)
        db.session.commit()
        flash('Authorized pick-up person has been updated.', 'success')
    else:
        flash('Error updating authorized pick-up person.', 'danger')
    return redirect(url_for('authorize_pickup'))

@app.route('/admin-edit-authorized-pickup/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_authorized_pickup(id):
    form = AuthorizePickUpForm()
    if form.validate_on_submit():
        authorized_pickup = AuthorizedPickUp.query.get(id)
        authorized_pickup.name = form.name.data
        authorized_pickup.telephone = form.telephone.data
        authorized_pickup.id_type = form.id_type.data
        authorized_pickup.id_number = form.id_number.data
        db.session.commit()
        flash('Authorized pick-up person has been updated.', 'success')
    else:
        flash('Error updating authorized pick-up person.', 'danger')
    return redirect(url_for('admin_authorize_pickup'))

@app.route('/prealerts', methods=['GET', 'POST'])
@login_required
def prealerts():
    form = PrealertForm()
    if form.validate_on_submit():
        file = form.invoice.data
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        else:
            unique_filename = None

        prealert = Prealert(
            user_id=current_user.id,
            carrier=form.carrier.data,
            tracking_number=form.tracking_number.data,
            description=form.description.data,
            value=form.value.data,
            invoice=unique_filename
        )
        db.session.add(prealert)
        db.session.commit()
        flash('Prealert added successfully.', 'success')
        return redirect(url_for('prealerts'))

    prealerts = Prealert.query.filter_by(user_id=current_user.id).all()
    return render_template('prealerts.html', form=form, prealerts=prealerts)

@app.route('/admin-prealerts', methods=['GET'])
@login_required
@admin_required
def admin_prealerts():
    if current_user.role != 'admin':
        return redirect(url_for('prealerts'))

    search_query = request.args.get('search', '')
    if search_query:
        search_filter = Prealert.query.join(User).filter(
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%')) |
            (Prealert.carrier.ilike(f'%{search_query}%')) |
            (Prealert.tracking_number.ilike(f'%{search_query}%'))
        )
        prealerts = search_filter.all()
    else:
        prealerts = Prealert.query.all()

    return render_template('admin_prealerts.html', prealerts=prealerts)



@app.route('/view-file/<filename>')
@login_required
def view_file(filename):
    try:
        file_ext = os.path.splitext(filename)[1].lower()
        file_url = url_for('show_image', filename=filename)
        return render_template('view_file.html', file_url=file_url, filename=filename, file_ext=file_ext)
    except Exception as e:
        flash(f"Error retrieving file: {str(e)}", 'danger')
        return render_template('404.html')

# @app.route('/view-file/<filename>')
# @login_required
# def get_image(filename):
#     try:
#         file_url = url_for('show_image', filename=filename)
#         file_ext = os.path.splitext(filename)[1].lower()
#         return render_template('view_file.html', file_url=file_url, filename=filename, file_ext=file_ext)
#     except Exception as e:
#         flash(f"Error retrieving file: {str(e)}", 'danger')
#         return render_template('404.html')

@app.route('/uploads/<filename>')
def show_image(filename):
    try:
        return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)
    except Exception as e:
        flash(f"Error retrieving file: {str(e)}", 'danger')
        return render_template('404.html')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", 'danger')
        return render_template('404.html')
    
    
@app.route('/admin/packages', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_packages():
    form = PackageForm()
    prealerts = Prealert.query.all()
    form.prealert_id.choices = [(0, '-- Select Prealert --')] + [(prealert.id, prealert.tracking_number) for prealert in prealerts]

    if form.validate_on_submit():
        prealert = Prealert.query.get(form.prealert_id.data) if form.prealert_id.data else None
        
        # Check if customer exists
        matching_customers = User.query.filter_by(first_name=form.first_name.data, last_name=form.last_name.data).all()
        
        if len(matching_customers) == 1:
            customer = matching_customers[0]
        elif len(matching_customers) > 1:
            # Try to match with prealert
            if prealert and prealert.user_id in [customer.id for customer in matching_customers]:
                customer = prealert.user
            else:
                reason = "Multiple customers with the same name."
                action_needed = "Manual verification required."
                add_to_action_required(form, reason, action_needed, user_id=None)
                flash('Multiple customers with the same name. Manual verification required.', 'warning')
                return redirect(url_for('manage_packages'))
        else:
            reason = "No matching customer found."
            action_needed = "Contact customer or create a new account."
            add_to_action_required(form, reason, action_needed, user_id=None)
            flash('No matching customer found. Manual action required.', 'warning')
            return redirect(url_for('manage_packages'))

        package = Package(
            tracking_number=prealert.tracking_number if prealert else form.tracking_number.data,
            first_name=prealert.user.first_name if prealert else form.first_name.data,
            last_name=prealert.user.last_name if prealert else form.last_name.data,
            item_number=f'MIS{str(Package.query.count() + 1).zfill(6)}',
            weight=prealert.weight if prealert else form.weight.data,
            description=prealert.description if prealert else form.description.data,
            status=form.status.data,
            sender=prealert.sender if prealert else form.sender.data,
            date_received=datetime.now(timezone.utc),
            invoice=secure_filename(form.invoice.data.filename) if form.invoice.data else None,
            user_id=customer.id
        )
        
        db.session.add(package)
        db.session.commit()

        # Handle "Held by Customs" status
        if form.status.data == 'Held by Customs':
            reason = "Package held by customs."
            action_needed = "Resolve customs issue."
            add_to_action_required(form, reason, action_needed, user_id=customer.id)
            flash('Package added with status "Held by Customs". Action required.', 'warning')
        
        flash('Package added successfully.', 'success')
        return redirect(url_for('manage_packages'))
    else:
        print("Form errors:", form.errors)
        
    packages = Package.query.all()
    return render_template('admin_packages.html', form=form, packages=packages)


def add_to_action_required(form, reason, action_needed, user_id):
    action_required = ActionRequired(
        tracking_number=form.tracking_number.data,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        item_number=f'MIS{str(ActionRequired.query.count() + 1).zfill(6)}',
        weight=form.weight.data,
        description=form.description.data,
        status=form.status.data,
        sender=form.sender.data,
        date_received=datetime.now(timezone.utc),
        invoice=secure_filename(form.invoice.data.filename) if form.invoice.data else None,
        reason=reason,
        action_needed=action_needed,
        user_id=user_id
    )
    db.session.add(action_required)
    db.session.commit()



@app.route('/admin/action-required', methods=['GET', 'POST'])
@login_required
@admin_required
def action_required():
    actions = ActionRequired.query.all()
    
    if request.method == 'POST':
        action_id = request.form.get('action_id')
        action = ActionRequired.query.get(action_id)
        
        # If resolved, move to Package table
        if 'resolve' in request.form:
            package = Package(
                tracking_number=action.tracking_number,
                first_name=action.first_name,
                last_name=action.last_name,
                item_number=action.item_number,
                weight=action.weight,
                description=action.description,
                status=action.status,
                sender=action.sender,
                date_received=action.date_received,
                invoice=action.invoice,
                user_id=action.user_id
            )
            db.session.add(package)
            db.session.delete(action)
            db.session.commit()
            flash('Action resolved and package moved to Package table.', 'success')
        elif 'update_status' in request.form:
            # Update the status of the action
            action.status = request.form.get('status')
            db.session.commit()
            flash('Status updated successfully.', 'success')
        elif 'update_user' in request.form:
            # Update the user of the action
            action.user_id = request.form.get('user_id')
            db.session.commit()
            flash('User updated successfully.', 'success')

        return redirect(url_for('action_required'))
    
    users = User.query.all()
    return render_template('admin_action_required.html', actions=actions, users=users)


@app.route('/admin/packages/<int:package_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = PackageForm(obj=package)
    prealerts = Prealert.query.all()
    form.prealert_id.choices = [(0, '-- Select Prealert --')] + [(prealert.id, prealert.tracking_number) for prealert in prealerts]

    if form.validate_on_submit():
        package.tracking_number = form.tracking_number.data
        package.first_name = form.first_name.data
        package.last_name = form.last_name.data
        package.weight = form.weight.data
        package.description = form.description.data
        package.status = form.status.data
        package.sender = form.sender.data

        try:
            package.date_received = form.date_received.data
        except ValueError:
            flash('Invalid date format. Please enter the date in YYYY-MM-DD format.', 'danger')
            return redirect(url_for('update_package', package_id=package_id))

        if form.invoice.data:
            package.invoice = secure_filename(form.invoice.data.filename)
            form.invoice.data.save(os.path.join(app.config['UPLOAD_FOLDER'], package.invoice))

        db.session.commit()
        flash('Package updated successfully.', 'success')
        return redirect(url_for('manage_packages'))
    else:
        print("Form errors:", form.errors)
        
    return render_template('admin_update_package.html', form=form, package=package)


@app.route('/api/prealert/<int:prealert_id>', methods=['GET'])
@login_required
@admin_required
def get_prealert(prealert_id):
    prealert = Prealert.query.get_or_404(prealert_id)
    return {
        'tracking_number': prealert.tracking_number,
        'first_name': prealert.user.first_name,
        'last_name': prealert.user.last_name,
        'description': prealert.description,
        'sender': prealert.carrier,  # Assuming sender is the carrier
        'invoice': prealert.invoice  # Assuming invoice is the filename
    }




@app.route('/packages')
@login_required
def view_packages():
    packages = Package.query.filter_by(user_id=current_user.id).all()
    return render_template('customer_packages.html', packages=packages)


    

###
# Login/Account Management Functions
###

# user_loader callback. This callback is used to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data  # Pass the raw password
            )
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user)
                # flash('Logged in successfully.', 'success')
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('No account found with that email. Please check and try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Here you would typically send an email with a password reset link
            flash('A password reset link has been sent to your email address.', 'info')
        else:
            flash('No account found with that email address.', 'danger')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)

@app.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    return render_template('dashboard_admin.html')

@app.route('/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('login'))
    return render_template('dashboard_customer.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403
