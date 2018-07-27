var regions = [];
var map = L.map('map').setView([4.624335, -74.063644], 13);

L.control.scale().addTo(map);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// 10km circle around bogota
function drawHf(coord) {
    L.circle(coord, $("#radius").val() * 1000).addTo(map)
}
// Update current drawing 
function drawSchools() {
    console.log("Printing %d points", regions.length);

    for(var i = 0; i < regions.length; i++) {
        //console.log(regions[i]);
        L.circle(regions[i], 2, {color: 'red'}).addTo(map);
    }
}

// jquery get request  
$("#script").on('click', function () {
    $.get({
        url:"/hf_compute", 
        data: { radius: $("#radius").val(),
                hospital: $("#hospital").val() },
        success: function(data) {
            console.log("get answer");
            regions = $.parseJSON(data);
            drawSchools();
            drawHf(regions[0])
        }
    });
});

// jquery get request  
function req_completion() {
    var cities = [];
    $.get({
        url:"/completion", 
        data: { text: $("#city").val(),
                hospital: $("#hospital").val()
        },
        success: function(data) {
            results = $.parseJSON(data);
            console.log(results);
            //cities.push(results["features"][0]["properties"]["city"]);
            //console.log(cities);
        }
    });
    return cities;
}

var choose_coord = {};

$( function() { 
    $('#city').autocomplete({

        source: function(request, response) {
            var cities = [];
            $.get({
                url:"/completion", 
                data: { text: $("#city").val() },
                success: function(data) {
                    results = $.parseJSON(data);
                    var cities = [];
                    var coord = {};
                    for(var i=0; i<results.length; i++) {
                        cities.push(results[i][0]);
                        coord[results[i][0]] = results[i][1];
                        //coord.push({key: results[i][0],
                        //           value: results[i][1]});
                    }
                    choose_coord = coord;
                    console.log(choose_coord);
                    response(cities);
                }
            });
         },

        select: function(event, ui) { 
                var c = choose_coord[ui.item.label];
                map.setView(c, 13);
        }
    });

});
