import json
import requests
import pandas as pd
import numpy as np
from flask import Flask, render_template, send_from_directory, request
from functions import grab, extract, assemble, similars, collect_artists, rec, bro_rec, create_graph, plot_graph

FLASK_PORT=41526

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def content():
    if request.method=='POST':
        band_name = request.form.get('bandName')
        bro = request.form.get('User')
        bro0= request.form.get('bro0')
        bro1= request.form.get('bro1')
        bro2= request.form.get('bro2')
        art1= request.form.get('art1')
        art2= request.form.get('art2')
        gra1= request.form.get('gra1')
        gra2= request.form.get('gra2')
        gra3= request.form.get('gra3')

        if band_name:
            sim=similars(band_name)
            dfhtml = sim.to_html(classes="table table-striped", index=False, justify= 'left')
            return render_template('index.html', dfhtml=dfhtml)
            # return render_template('index.html', df=sim)
        elif bro:
            my_artists=collect_artists()
            dfhtml = my_artists[bro].to_html(classes="table table-striped", index=False, justify= 'left')
            return render_template('index.html', dfhtml=dfhtml)
        elif bro0:
            my_artists=collect_artists()
            dfhtml = rec(bro0, my_artists).to_html(classes="table table-striped", index=False, justify= 'left')
            return render_template('index.html', dfhtml=dfhtml)
        elif bro1:
            my_artists=collect_artists()
            dfhtml = bro_rec(bro1, bro2, my_artists).to_html(classes="table table-striped", index=False, justify= 'left')
            return render_template('index.html', dfhtml=dfhtml)
        elif art1:
            sim=similars(art1).merge(similars(art2), on="Artist", how='inner')
            dfhtml = sim.to_html(classes="table table-striped", index=False, justify= 'left')
            return render_template('index.html', dfhtml=dfhtml)
        elif gra1:
            gra2=int(gra2)
            gra3=float(gra3)
            my_artists=collect_artists()
            edges=create_graph(gra1, my_artists, gra2, gra3)
            df=pd.DataFrame(edges)
            dfhtml = df.to_html(classes="table table-striped", index=False, justify= 'left')
            plot_graph(gra1, my_artists, edges, gra2)
            return render_template('index.html', dfhtml=dfhtml)


    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=FLASK_PORT, debug=True)
