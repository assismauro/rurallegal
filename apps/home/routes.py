# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.home.ui_projectLocation as ui_projectLocation
import apps.home.ui_plantdistribution as ui_plantdistribution
import apps.home.dbquery as dbquery
import apps.home.ui_combination as ui_combination
import apps.home.ui_projectEnd as ui_projectEnd
from flask import session
from apps.home import helper
from flask_login import current_user


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/callback/<endpoint>')
@login_required
def route_callback(endpoint):
    if endpoint == 'getDistribution':
        return ui_plantdistribution.getPlantDistribution(session['_projeto_id'])
    args = request.args
    callerID = args.get('callerID')
    if callerID == 'mapSP':
        return ui_projectLocation.getMapSP()
    idFito = int(args.get('idFito')) if callerID in ['fito_ecologica', 'saveProject'] else -1
    latlong = args.get('latlong')
    CAR = args.get('CAR')
    if endpoint == 'updateFormData':
        try:
            idMunicipio = int(args.get('idMunicipio'))
        except:
            idMunicipio = -1
        return ui_projectLocation.getMapFitoMunicipio(callerID,
                                                      idMunicipio,
                                                      idFito,
                                                      latlong,
                                                      CAR)
    elif endpoint == 'saveProject':
        projectName = args.get('ProjectName')
        if projectName == '':
            session['_projeto_id'] = 97
            return "Ok"
        projeto_id = ui_projectLocation.saveProject(session['_user_id'],
                                                    args.get('ProjectName'),
                                                    args.get('ProjectArea'),
                                                    args.get('PropertyArea'),
                                                    idFito,
                                                    latlong,
                                                    CAR)
        session['_projeto_id'] = projeto_id
    elif endpoint == 'help':
        return helper.getHelpText(args.get('id'))
    return "Ok"


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if template.find('.html') > -1:
            # Detect the current page
            segment = helper.get_segment(request)
            # if segment.startswith('testeJinja'):
            if segment == 'rsp-projectStart.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-projectStart'))
            if segment == 'rsp-selectProject.html':
                return render_template("home/" + template,
                                       projects=dbquery.getListDictResultset(
                                           f"select descProjeto as caption, id from Projeto p "
                                           f"where idUser = {current_user.id}"
                                           f"order by descProjeto")
                                       , **helper.getFormText('rsp-selectProject'))

            if segment == 'rsp-projectLocation.html':
                projectId = (int(request.args['id']) if 'id' in request.args else -1)
                #if projectId > -1:
                return render_template("home/" + template,
                                       municipios=ui_projectLocation.getListaMunicipios()
                                       , fito_municipios=ui_projectLocation.getListaFito(None)
                                       , **helper.getFormText('rsp-projectLocation')
                                       # , map=ui_projectLocation.getMapSP()
                                       )

            elif segment == 'rsp-goal.html':
                return render_template("home/" + template,
                                       goals=dbquery.getListDictResultset(
                                           f"select desFinalidade as caption, id "  # desFinalidade: typo
                                           f"from Finalidade "
                                           f"order by orderby")
                                       , **helper.getFormText('rsp-goal'))

            elif segment == 'rsp-plantDistribution.html':
                # TODO: number of n??mero de m??dulos fiscais validation
                idFinalidade = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idFinalidade = {idFinalidade} "
                                   f"where id = {session['_projeto_id']}")
                return render_template("home/" + template
                                       , **helper.getFormText('rsp-projectLocation'))


            elif segment == 'rsp-relief.html':
                idModeloPlantio = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idModeloPlantio = {idModeloPlantio} "
                                   f"where id = {session['_projeto_id']}")
                return render_template("home/" + template
                                       , **helper.getFormText('rsp-relief'))

            elif segment == "rsp-mecanization.html":
                idTopografia = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idTopografia = {idTopografia} "
                                   f"where id = {session['_projeto_id']}")

                return render_template("home/" + template,
                                       mecanization=dbquery.getListDictResultset(
                                           f"select nomeMecanizacao as caption, id "  # desFinalidade: typo
                                           f"from MecanizacaoNivel "),
                                       **helper.getFormText('rsp-mecanization'))

            elif segment == 'rsp-combinations.html':
                # return render_template("home/rsp-relief.html", segment="rsp-relief.html")
                idMecanizacaoNivel = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idMecanizacaoNivel = {idMecanizacaoNivel} "
                                   f"where id = {session['_projeto_id']}")

                combinations, strips, noData = ui_combination.getCombinations(session['_projeto_id'])
                return render_template("home/" + template,
                                       strips=strips,
                                       combinations=combinations,
                                       noData=noData)

            elif segment == 'rsp-projectEnd.html':
                #                ui_projectData.updateProjectData(session['_projeto_id'], request.args['id'])
                projectData, combinations = ui_projectEnd.getProjectData(session['_projeto_id'], request.args['id'])
                return render_template("home/" + template, combinations=combinations, **projectData)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as e:
        return render_template('home/page-500.html', errorMsg=str(e)), 500
