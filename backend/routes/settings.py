from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Settings, db

settings_bp = Blueprint('settings', __name__)

# Default settings
DEFAULT_SETTINGS = {
    'company_name': 'TEX-SARTHI',
    'company_address': '',
    'company_phone': '',
    'company_email': '',
    'company_gst': '',
    'tax_rate': '18',
    'currency': 'INR',
    'invoice_prefix': 'INV',
    'order_prefix': 'ORD',
    'delivery_prefix': 'DEL',
    'low_stock_threshold': '10',
    'auto_generate_invoice': 'true',
    'auto_generate_delivery': 'false',
    'backup_frequency': 'daily',
    'email_notifications': 'true',
    'sms_notifications': 'false'
}

@settings_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    try:
        # Get all settings
        settings = Settings.query.all()
        
        # Convert to dictionary
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = setting.value
        
        # Add default settings if not present
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings_dict:
                settings_dict[key] = value
        
        return jsonify({
            'settings': settings_dict,
            'message': 'Settings retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch settings'}), 500

@settings_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update or create settings
        for key, value in data.items():
            setting = Settings.query.filter_by(key=key).first()
            
            if setting:
                setting.value = str(value)
            else:
                setting = Settings(
                    key=key,
                    value=str(value),
                    description=f'Setting for {key}'
                )
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update settings'}), 500

@settings_bp.route('/settings/<string:key>', methods=['GET'])
@jwt_required()
def get_setting(key):
    try:
        setting = Settings.query.filter_by(key=key).first()
        
        if not setting:
            # Return default value if setting doesn't exist
            default_value = DEFAULT_SETTINGS.get(key, '')
            return jsonify({
                'key': key,
                'value': default_value,
                'isDefault': True
            }), 200
        
        return jsonify({
            'key': setting.key,
            'value': setting.value,
            'description': setting.description,
            'isDefault': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch setting'}), 500

@settings_bp.route('/settings/<string:key>', methods=['PUT'])
@jwt_required()
def update_setting(key):
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({'error': 'Value is required'}), 400
        
        setting = Settings.query.filter_by(key=key).first()
        
        if setting:
            setting.value = str(data['value'])
        else:
            setting = Settings(
                key=key,
                value=str(data['value']),
                description=data.get('description', f'Setting for {key}')
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'key': setting.key,
            'value': setting.value,
            'message': 'Setting updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update setting'}), 500

@settings_bp.route('/settings/<string:key>', methods=['DELETE'])
@jwt_required()
def delete_setting(key):
    try:
        setting = Settings.query.filter_by(key=key).first()
        
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
        
        # Don't allow deletion of default settings
        if key in DEFAULT_SETTINGS:
            return jsonify({'error': 'Cannot delete default setting'}), 400
        
        db.session.delete(setting)
        db.session.commit()
        
        return jsonify({'message': 'Setting deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete setting'}), 500

@settings_bp.route('/settings/reset', methods=['POST'])
@jwt_required()
def reset_settings():
    try:
        # Delete all custom settings (keep only default ones)
        custom_settings = Settings.query.filter(
            ~Settings.key.in_(DEFAULT_SETTINGS.keys())
        ).all()
        
        for setting in custom_settings:
            db.session.delete(setting)
        
        # Reset default settings to their default values
        for key, value in DEFAULT_SETTINGS.items():
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Settings(
                    key=key,
                    value=value,
                    description=f'Default setting for {key}'
                )
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'Settings reset to defaults successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset settings'}), 500

@settings_bp.route('/settings/backup', methods=['POST'])
@jwt_required()
def backup_settings():
    try:
        # Get all settings
        settings = Settings.query.all()
        
        # Create backup data
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'settings': {}
        }
        
        for setting in settings:
            backup_data['settings'][setting.key] = {
                'value': setting.value,
                'description': setting.description,
                'created_at': setting.created_at.isoformat() if setting.created_at else None,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            }
        
        return jsonify({
            'backup': backup_data,
            'message': 'Settings backup created successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to create settings backup'}), 500

@settings_bp.route('/settings/restore', methods=['POST'])
@jwt_required()
def restore_settings():
    try:
        data = request.get_json()
        
        if not data or 'backup' not in data:
            return jsonify({'error': 'Backup data is required'}), 400
        
        backup_data = data['backup']
        
        if 'settings' not in backup_data:
            return jsonify({'error': 'Invalid backup format'}), 400
        
        # Clear existing settings
        Settings.query.delete()
        
        # Restore settings from backup
        for key, setting_data in backup_data['settings'].items():
            setting = Settings(
                key=key,
                value=setting_data['value'],
                description=setting_data.get('description', f'Setting for {key}')
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'Settings restored successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to restore settings'}), 500
