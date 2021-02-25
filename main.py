import time
import routeros_api
from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
connection = routeros_api.RouterOsApiPool('gateway.loc', username='vpn-switcher', password='1', plaintext_login=True)

status_whitelist = [
    'id',
    'name',
    'type',
    'last-link-down-time',
    'last-link-up-time',
    'running',
    'disabled',
    'comment',
    'Ingress',
    'Egress'
]

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        state = 'off' if is_enabled(request.form['if_id']) else 'on'
        flash(f"Interface {request.form['if_name']} ({request.form['if_id']}) switched {state}.")
        if_switch(request.form['if_id'])

    # status = if_status()
    return render_template(
        'index.j2',
        if_status=if_status()
    )

def is_enabled(id):
    api = connection.get_api()
    res = api.get_resource('/interface')
    vpn_interface = res.get(id=id)[0]
    return True if vpn_interface["disabled"] == "false" else False

def if_status():
    api = connection.get_api()
    res = api.get_resource('/interface')
    vpn_interface = res.get(comment="bgp-vpn")
    ret = list()
    for ifc in vpn_interface:
        ifc["Ingress"] = f"{int(ifc['rx-byte']) / 1024 / 1024 / 1024:.2f} GB"
        ifc["Egress"] = f"{int(ifc['tx-byte']) / 1024 / 1024 / 1024:.2f} GB"
        new_if = {k: ifc[k] for k in status_whitelist}
        ret.append(new_if)


    return ret

def if_switch(id):
    cur_state = is_enabled(id)
    api = connection.get_api()
    res = api.get_resource('/interface')
    vpn_interface = res.get(id=id)[0]
    if vpn_interface["disabled"] == "true":
        res.set(id=vpn_interface["id"], disabled="no")
    else:
        res.set(id=vpn_interface["id"], disabled="yes")
    while cur_state == is_enabled(id):
        print("Not ready!")
        time.sleep(0.2)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
