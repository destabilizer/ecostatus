// var $ = require('jquery');
// var s = require('smoothie');

var data = [];
var datatypes = [];
var charts = [];
var devices = [];
var devices_style = [];
var delay = 1000;

$.getJSON('/api/control', function(jsondata){
    d = JSON.parse(jsondata);
    datatypes = d['datatypes'];
    devices = d['visible_devices'];
    var datl = datatypes.length;
    var devl = devices.length;
    for (var dev = 0; dev < devl; dev++){
    }
    for (var i = 0; i < datl; i++){
	var chart = new SmoothieChart();
	chart.streamTo(document.getElementById(datatypes[i]), delay);
	chart.addTimeSeries(dat);
	for (var dev = 0; dev < devl; dev++){
	    var dat = new TimeSeries();
	    data.push(dat);
	    //style
	    var h = 360*(dev/devl);    // hue
	    ds = {strokeStyle: 'hsl('+h+',1.0,0.5)', fillStyle: 'hsla('+h+',1.0,0.5,0.3)', lineWidth: 3}
	    //add data and style
	    chart.addTimeSeries(dat, ds);
	}
	charts.push(chart);
    }
});


function update_data() {
    $.getJSON('/api/data', function(jsondata){
	dat = JSON.parse(jsondata)
	cd = dat['current']
	cl = charts.length;
	dl = devices.length;
	for (var c = 0; c < cl; c++){
	    dt = datatypes[c];
	    chart = charts[c];	    
	    for (var d = 0; d < dl; d++){
		dev = devices[d];
		dat = data[c*dl+d];
		dat.append(new Data().getTime(), cd[dev][dt])
	    }
	}
    });
}

// setInterval(update_data, delay);
