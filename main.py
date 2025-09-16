from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timezone
import os

app = Flask(__name__)

# Webhook Konfiguration über Env mit Fallback
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1417158963233030174/fPYxvwbsYZ7hLGZ7xIE3sfq2zbwg6mT-EAeGnh4uaeT6eMuIHDpFy2vWhBK_p6Flg-Y5")
DISCORD_WEBHOOK_ENABLED = os.getenv("DISCORD_WEBHOOK_ENABLED", "true").lower() == "true"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_waitlist', methods=['POST'])
def submit_waitlist():
    try:
        # Get form data
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Role translations for better display
        role_translations = {
            'ceo': 'CEO/Founder',
            'cto': 'CTO/Technical Lead',
            'operations': 'Operations Manager',
            'customer-success': 'Customer Success',
            'sales': 'Sales Manager',
            'marketing': 'Marketing Manager',
            'it': 'IT Administrator',
            'other': 'Other'
        }

        # Interest translations
        interest_translations = {
            'save-time': 'Save time on email responses',
            '24-7-support': '24/7 automated customer support',
            'multilingual': 'Multi-language support',
            'integration': 'Email system integration',
            'analytics': 'Email performance analytics',
            'security': 'Enterprise security features'
        }

        # Industry translations
        industry_translations = {
            'technology': 'Technology & Software',
            'healthcare': 'Healthcare & Medical',
            'finance': 'Financial Services',
            'education': 'Education & Training',
            'retail': 'Retail & E-commerce',
            'manufacturing': 'Manufacturing',
            'consulting': 'Consulting & Professional Services',
            'real-estate': 'Real Estate',
            'hospitality': 'Hospitality & Tourism',
            'other': 'Other Industry'
        }

        role_display = role_translations.get(data.get('role', ''), data.get('role', 'Not specified'))
        interest_display = interest_translations.get(data.get('interest', ''), data.get('interest', 'Not specified'))
        industry_display = industry_translations.get(data.get('industry', ''), data.get('industry', 'Not specified'))

        # Create beautiful Discord embed
        embed = {
            "title": "🚀 New AutoEmailAI Waitlist Signup!",
            "description": "**A new prospect wants to be notified about the launch!**",
            "color": 0x14B8A6,  # Teal color
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "thumbnail": {
                "url": "https://cdn-icons-png.flaticon.com/512/2991/2991148.png"
            },
            "fields": [
                {
                    "name": "👤 Contact Person",
                    "value": f"**{data.get('fullName', 'Not provided')}**",
                    "inline": True
                },
                {
                    "name": "📧 Email Address",
                    "value": f"`{data.get('email', 'Not provided')}`",
                    "inline": True
                },
                {
                    "name": "🏢 Company",
                    "value": f"**{data.get('company', 'Not provided')}**",
                    "inline": True
                },
                {
                    "name": "🏭 Industry",
                    "value": f"{industry_display}",
                    "inline": True
                },
                {
                    "name": "💼 Position",
                    "value": f"{role_display}",
                    "inline": True
                },
                {
                    "name": "❤️ Primary Interest",
                    "value": f"{interest_display}",
                    "inline": True
                },
                {
                    "name": "📝 Additional Notes",
                    "value": f"{data.get('notes', 'No additional notes provided')}",
                    "inline": False
                },
                {
                    "name": "🕐 Signup Time",
                    "value": f"`{datetime.now().strftime('%d.%m.%Y at %H:%M:%S')}`",
                    "inline": True
                }
            ],
            "footer": {
                "text": "AutoEmailAI Waitlist System | Developed by CodeProTech",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/25/25231.png"
            },
            "author": {
                "name": "AutoEmailAI Dashboard",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/8943/8943377.png"
            }
        }

        # Main content message
        company_name = data.get('company', 'a company')
        content_message = f"🎯 **New waitlist signup from {company_name}!**"

        # Discord webhook payload
        discord_data = {
            "content": content_message,
            "embeds": [embed],
            "username": "AutoEmailAI Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
        }

        # Wenn Webhook deaktiviert oder URL leer: Erfolg simulieren (z.B. in Dev/Test)
        if not DISCORD_WEBHOOK_ENABLED or not DISCORD_WEBHOOK_URL:
            print("[INFO] Discord webhook disabled or missing URL. Skipping network call.")
            return jsonify({"success": True, "message": "Successfully added to waitlist! 🎉"})

        # Discord webhook senden mit besserer Fehlerbehandlung
        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=discord_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            print(f"[DEBUG] Discord response status: {response.status_code}")
            print(f"[DEBUG] Discord response text: {response.text}")

            if response.status_code == 204:
                return jsonify({"success": True, "message": "Successfully added to waitlist! 🎉"})
            else:
                print(f"Discord Webhook Error: {response.status_code} - {response.text}")
                # Trotzdem Erfolg zurückgeben, da die Daten empfangen wurden
                return jsonify({"success": True, "message": "Added to waitlist! (Notification may be delayed)"})

        except requests.exceptions.Timeout:
            print("Discord webhook timeout")
            return jsonify({"success": True, "message": "Added to waitlist! (Notification may be delayed)"})
        except requests.exceptions.RequestException as e:
            print(f"Discord webhook request error: {str(e)}")
            return jsonify({"success": True, "message": "Added to waitlist! (Notification may be delayed)"})

    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while processing your request"}), 500

# if __name__ == '__main__':
#     app.run(debug=False, port=3000, host='0.0.0.0')
