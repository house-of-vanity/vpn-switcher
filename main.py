import time
import routeros_api
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
connection = routeros_api.RouterOsApiPool('gateway.loc', username='vpn-switcher', password='1', plaintext_login=True)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if_switch(request.form['if_id'])
    # status = if_status()
    return render_template(
        'index.j2',
        if_status=if_status()
    )

def if_status():
    api = connection.get_api()
    res = api.get_resource('/interface')
    vpn_interface = res.get(comment="bgp-vpn")
    for ifc in vpn_interface:
        ifc["Ingress"] = f"{int(ifc['rx-byte']) / 1024 / 1024 / 1024:.2f} GB"
        ifc["Egress"] = f"{int(ifc['tx-byte']) / 1024 / 1024 / 1024:.2f} GB"
    return vpn_interface

def if_switch(id):
    api = connection.get_api()
    res = api.get_resource('/interface')
    vpn_interface = res.get(id=id)[0]
    if vpn_interface["disabled"] == "true":
        res.set(id=vpn_interface["id"], disabled="no")
    else:
        res.set(id=vpn_interface["id"], disabled="yes")
    time.sleep(2)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
