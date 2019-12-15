$(function () {
    //Configuration des datepicker JqueryUI
    var dateFormat = "yy/mm/dd"
    var datepickerOptions = {
        defaultDate: "+1w",
        dateFormat: dateFormat,
        showAnim: "fadeIn",
        yearRange: "1985:" + new Date().getFullYear().toString(),
        changeMonth: true,
        changeYear: true
    }

    function getDate(element) {
        var date;
        try {
            date = $.datepicker.parseDate(dateFormat, element.value);
        } catch (error) {
            date = null;
        }

        return date;
    }

    //Pour la moyenne des salaires par genre pour la vue Analyst, on ne veut pas que la date de fin puisse être avant la date de début
    var from = $("#moy-salary-from_date")
        .datepicker(datepickerOptions)
        .on("change", function () {
            to.datepicker("option", "minDate", getDate(this));
        }),
        to = $("#moy-salary-to_date").datepicker(datepickerOptions)
            .on("change", function () {
                from.datepicker("option", "maxDate", getDate(this));
            });

    // GESTION DES SUBMITS POUR CHAQUE FORMULAIRE

    $('#form-all-managers').submit(function (e) {
        var formData = {
            'dept_no': $('select[name=dept_no]').val()
        };

        $.ajax({
            type: 'GET',
            url: '/all_managers/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-all-managers button').empty()
                $('#form-all-managers button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
            }
        })
            .done(function (data) {
                console.log(data);

                $('#all-managers-result').empty()
                data.employees_names.forEach(element => {
                    $('#all-managers-result').append('<li>' + element.first_name + ' ' + element.last_name + '</li>')
                });

                $('#form-all-managers button').remove('span')
                $('#form-all-managers button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-all-employees').submit(function (e) {
        var formData = {
            'dept_no2': $('select[name=dept_no2]').val(),
            'title': $('select[name=title]').val()
        };

        $.ajax({
            type: 'GET',
            url: '/all_employees/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                $('#all-employees-result').empty()

                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-all-employees button').empty()
                $('#form-all-employees button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
            }
        })
            .done(function (data) {
                console.log(data);

                if (data.dept_employees_names.length > 0) {
                    data.dept_employees_names.forEach(element => {
                        $('#all-employees-result').append('<li>' + element.first_name + ' ' + element.last_name + '</li>')
                    });
                }
                else {
                    $('#all-employees-result').append('Pas de résultats')
                }

                $('#form-all-employees button').remove('span')
                $('#form-all-employees button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-all-salaries').submit(function (e) {
        var formData = {
            'emp_emp_no': $('input[name=emp_emp_no]').val()
        };

        $.ajax({
            type: 'GET',
            url: '/all_salaries/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-all-salaries button').empty()
                $('#form-all-salaries button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')

                $('#all-salaries-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);
                if (data.labels.length > 0 && data.values.length > 0) {
                    $('#all-salaries-result').append('<canvas id="all-salaries-bar-chart"></canvas>')

                    //Définition des paramètres de l'histogramme Chart.js
                    var barChartData = {
                        labels: data.labels,
                        datasets: [{
                            label: 'Salaires',
                            backgroundColor: randomColor({ hue: 'blue', luminosity: 'light' }),
                            borderWidth: 1,
                            data: data.values
                        }]
                    };

                    var ctx = document.getElementById('all-salaries-bar-chart').getContext('2d');
                    window.myBar = new Chart(ctx, {
                        type: 'bar',
                        data: barChartData,
                        options: {
                            responsive: true,
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Histogramme des salaires par période'
                            },
                            tooltips: {
                                mode: 'index',
                            }
                        }
                    });
                }
                else {
                    $('#all-salaries-result').append('Pas de résultats')
                }

                $('#form-all-salaries button').remove('span')
                $('#form-all-salaries button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-dept-titles').submit(function (e) {
        var formData = {
            'dept_no3': $('select[name=dept_no3]').val(),
            'from_date_year': $('input[name=from_date_year]').val(),
            'from_date_month': $('input[name=from_date_month]').val()
        };

        $.ajax({
            type: 'GET',
            url: '/dept_titles_date/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-dept-titles button').empty()
                $('#form-dept-titles button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')

                $('#dept-titles-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);
                if (data.labels.length > 0) {
                    $('#dept-titles-result').append('<canvas id="dept-titles-bar-chart"></canvas>')

                    //Définition des paramètres de l'histogramme empilé Chart.js
                    var colors = randomColor({ count: data.datasets.length, hue: 'blue', luminosity: 'light' })
                    var datasets = []
                    var count = 0

                    data.datasets.forEach(function (label) {
                        var data2 = []
                        for (var key in data.values) {
                            data.values[key].forEach(function (value) {
                                if (value.title == label) {
                                    data2.push(value.count)
                                }
                            })
                        }
                        var dataset = {
                            label: label,
                            backgroundColor: colors[count],
                            data: data2
                        }
                        count++
                        datasets.push(dataset)
                    })

                    var barChartData = {
                        labels: data.labels,
                        datasets: datasets
                    };

                    var ctx = document.getElementById('dept-titles-bar-chart').getContext('2d');
                    window.myBar = new Chart(ctx, {
                        type: 'bar',
                        data: barChartData,
                        options: {
                            title: {
                                display: true,
                                text: 'Histogramme empilé des titres des collaborateurs ayant intégré le département - ' + formData.from_date_year + '/' + formData.from_date_month
                            },
                            tooltips: {
                                mode: 'index',
                                intersect: false
                            },
                            responsive: true,
                            scales: {
                                xAxes: [{
                                    ticks: {
                                        autoSkip: true
                                    },
                                    stacked: true,
                                }],
                                yAxes: [{
                                    stacked: true
                                }]
                            }
                        }
                    });
                }
                else {
                    $('#dept-titles-result').append('Pas de résultats')
                }

                $('#form-dept-titles button').remove('span')
                $('#form-dept-titles button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-moy-salary').submit(function (e) {
        var formData = {
            'from_date': $('input[name=moy-salary-from_date]').val(),
            'to_date': $('input[name=moy-salary-to_date]').val()
        };

        $.ajax({
            type: 'GET',
            url: '/moy_salaire/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-moy-salary button').empty()
                $('#form-moy-salary button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                
                $('#moy-salary-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);

                if (data.labels.length > 0 && data.values.length > 0) {
                    $('#moy-salary-result').append('<canvas id="moy-salary-doughnut"></canvas>')

                    //Définition des paramètres du doughnut Chart.js
                    var config = {
                        type: 'doughnut',
                        data: {
                            datasets: [{
                                data: data.values,
                                backgroundColor: randomColor({ count: 2, hue: 'blue', luminosity: 'light' }),
                                label: 'Dataset 1'
                            }],
                            labels: data.labels
                        },
                        options: {
                            responsive: true,
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Salaire moyen par genre, du ' + formData.from_date + ' au ' + formData.to_date
                            },
                            animation: {
                                animateScale: true,
                                animateRotate: true
                            }
                        }
                    };

                    var ctx = document.getElementById('moy-salary-doughnut').getContext('2d');
                    window.myDoughnut = new Chart(ctx, config);
                }
                else {
                    $('#moy-salary-result').append('Pas de résultats')
                }

                $('#form-moy-salary button').remove('span')
                $('#form-moy-salary button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-avg-salary-title-hire-date').submit(function (e) {
        var formData = {
            'from_date_year': $('input[name=from_date_year2]').val(),
            'from_date_month': $('input[name=from_date_month2]').val()
        };
        $.ajax({
            type: 'GET',
            url: '/avg_salary_title_hire_date/',
            data: formData, 
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-avg-salary-title-hire-date button').empty()
                $('#form-avg-salary-title-hire-date button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                
                $('#avg-salary-title-hire-date-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);

                if (data.labels.length > 0) {
                    $('#avg-salary-title-hire-date-result').append('<canvas id="avg-salary-title-hire-date-bar-chart"></canvas>')

                    //Définition des paramètres de l'histogramme empilé Chart.js
                    var colors = randomColor({ count: data.datasets.length, hue: 'blue', luminosity: 'light' })
                    var datasets = []
                    var count = 0

                    data.datasets.forEach(function (label) {
                        var data2 = []
                        data.values.forEach(function (value) {
                            if (value.title == label) {
                                data2.push(value.moy)
                            }
                        })
                        var dataset = {
                            label: label,
                            backgroundColor: colors[count],
                            data: data2
                        }
                        count++
                        datasets.push(dataset)
                    })

                    var barChartData = {
                        labels: data.labels,
                        datasets: datasets
                    };

                    var ctx = document.getElementById('avg-salary-title-hire-date-bar-chart').getContext('2d');
                    window.myBar = new Chart(ctx, {
                        type: 'bar',
                        data: barChartData,
                        options: {
                            title: {
                                display: true,
                                text: 'Histogramme empilé des salaires moyens par titre et par ancienneté - ' + formData.from_date_year + '/' + formData.from_date_month
                            },
                            tooltips: {
                                mode: 'index',
                                intersect: false
                            },
                            responsive: true,
                            scales: {
                                xAxes: [{
                                    ticks: {
                                        autoSkip: true
                                    },
                                    stacked: true,
                                }],
                                yAxes: [{
                                    stacked: true
                                }]
                            }
                        }
                    });
                }
                else {
                    $('#avg-salary-title-hire-date').append('Pas de résultats')
                }
                
                $('#form-avg-salary-title-hire-date button').remove('span')
                $('#form-avg-salary-title-hire-date button').text('Valider')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-db-stats').submit(function (e) {
        var formData = {};

        $.ajax({
            type: 'GET',
            url: '/admin_db_stats/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-db-stats button').empty()
                $('#form-db-stats button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                
                $('#db-stats-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);

                //Construction de tous les éléments HTML à afficher en utilisant les données renvoyées par la requête GET, qu'on va ajouter en jQuery à l'élément du tableau de bord
                var chunks_employees = '<li>Nombre de chunks pour employees : <b>' + data.collStats_employees.nchunks + '</b></li>'
                var chunks_departments = '<li>Nombre de chunks pour departments : <b>' + data.collStats_departments.nchunks + '</b></li>'
                var explain_find_employees = '<li>Temps de réponse pour employees.find() : <b>' + data.explain_find_employees.executionStats.executionTimeMillis + ' ms</b></li>'
                var explain_find_departments = '<li>Temps de réponse pour departments.find() : <b>' + data.explain_find_departments.executionStats.executionTimeMillis + ' ms</b></li>'
                var objects = '<li>Nombre de documents dans la base de données : <b>' + data.dbStats.objects + '</b></li>'
                var dataSize = '<li>Taille totale de la base de données : <b>' + data.dbStats.dataSize / 10 ** 6 + ' Mo</b></li>'
                var shard_number = '<th id="shard-number" scope="col">#</th>'
                var shard_name = '<th id="shard-name" scope="col">Shard</th>'
                var shard_objects = '<th id="shard-objects" scope="col">Documents</th>'
                var host = '<th id="host" scope="col">Hôte</th>'
                var thead = '<thead><tr>' + shard_number + shard_name + host + shard_objects + '</tr></thead>'
                var tbody = '<tbody></tbody>'
                var table_sharding = '<table id="table-db-stats" class="table">' + thead + tbody + '</table>'
                var div1 = '<div id="dbStats">' + chunks_employees + chunks_departments + explain_find_employees + explain_find_departments + objects + dataSize + '</div>'
                $('#db-stats-result').append(div1)
                $('#db-stats-result').append(table_sharding)

                var count = 1

                data.listShards.shards.forEach(function (shard) {
                    var objects = data.dbStats.raw[shard.host].objects
                    var shard_info = '<td>' + shard._id + '</td><td>' + shard.host + '</td><td>' + objects + '</td>'
                    var row = '<tr><th scope="row">' + count + '</th>' + shard_info + '</tr>'
                    $('#table-db-stats tbody').append(row)
                    count++
                })

                $('#form-db-stats button').remove('span')
                $('#form-db-stats button').text('Calculer')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit
        e.preventDefault();
    });

    $('#form-sharding-state').submit(function (e) {
        var formData = {};

        $.ajax({
            type: 'GET',
            url: '/admin_sharding_state/',
            data: formData,
            dataType: 'json',
            encode: true,
            beforeSend: function () {
                //On affiche un spinner sur le bouton de submit, pour signifier que le serveur est en train de récupérer les données
                $('#form-sharding-state button').empty()
                $('#form-sharding-state button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                
                $('#sharding-state-result').empty()
            }
        })
            .done(function (data) {
                console.log(data);

                $('#sharding-state-result').append('<canvas id="sharding-state-doughnut"></canvas>')

                //Définition des paramètres du doughnut Chart.js
                var config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data.values,
                            backgroundColor: randomColor({ count: data.labels.length, hue: 'blue', luminosity: 'light' }),
                            label: 'Dataset 1'
                        }],
                        labels: data.labels
                    },
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Nombre de documents par shard'
                        },
                        animation: {
                            animateScale: true,
                            animateRotate: true
                        }
                    }
                };

                var ctx = document.getElementById('sharding-state-doughnut').getContext('2d');
                window.myDoughnut = new Chart(ctx, config);

                $('#form-sharding-state button').remove('span')
                $('#form-sharding-state button').text('Calculer')
            });
        //Empêcher le comportement par défaut du <form> qui rafraîchit la page après submit   
        e.preventDefault();
    });

    $('#disconnect').on('click', function () {
        window.location.href = '/logout/'
    });
});