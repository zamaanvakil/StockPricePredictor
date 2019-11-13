from flask import Flask, render_template, url_for, request, redirect

import monte_carlo as mc
import shutil
import os
app = Flask(__name__)


@app.route('/')
def index():
    if os.path.exists('static/images/output'):
        shutil.rmtree('static/images/output')

    return render_template('form.html')

@app.route('/display',methods = ['POST','GET'])
def display():
    if request.method == "POST" :
            ticker1 = request.form['ticker']
            sim_days1 = request.form['sim_days']
            sim_num1 = request.form['sim_num']

            sim = mc.monte_carlo(ticker1)
            name1,name2 = sim.plot_historical_data()
            a1,b1,name3,name4 = sim.brownian_motion(int(sim_days1,10),int(sim_num1,10))


            if name1 != -1:
                return render_template('display.html', a=a1,b=b1,n1=name1,n2=name2,n3=name3,n4=name4,company_name= sim.company_name,se_name=sim.se_name)
            else:
                return render_template('display_error.html')

            
    else :
    	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)