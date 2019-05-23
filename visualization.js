var $ = require('./node_modules/jquery');
var S = require('./node_modules/smoothie');
var convert = require('./node_modules/color-convert')
//var $n = require('./node_modules/notify')

var tsstack = [];
var datatypes = [];
var datl = 0;
var charts = [];
var chtl = 0;
var devices = [];
var devl = 0;
var delay = 1000;

var device_styles = [];

function generate_style(n, total){
    var h = 360*(n/total);
    var rgb = convert.hsl.rgb(h, 100, 50);
    var hex = convert.rgb.hex(rgb);
    var r = rgb[0]; var g = rgb[1]; var b = rgb[2];
    var style = {color_hex: hex,
                 strokeStyle: 'rgb('+r+','+g+','+b+')', 
                 fillStyle: 'rgba('+r+','+g+','+b+','+'0.3)', 
                 lineWidth: 3};
    return style;
}

function generate_styles(){
    for (var d = 0; d < devl; d++){
        var ds = generate_style(d, devl);
        device_styles.push(ds);
    }
}

function colorify_device_names(){
    for (var d = 0; d < devl; d++){
        var dev = devices[d];
        var devname = document.getElementById('device_name_'+dev);
        devname.style.color = '#'+device_styles[d].color_hex
    }
}


$.getJSON('/api/control', function(d){
    datatypes = d['datatypes'];
    devices = d['visible_devices'];
    datl = datatypes.length;
    devl = devices.length;
    generate_styles();
    colorify_device_names();
    for (var i = 0; i < datl; i++){
	    var chart = new S.SmoothieChart();
	    chart.streamTo(document.getElementById(datatypes[i]), delay);
	    for (var d = 0; d < devl; d++){
	        var ts = new S.TimeSeries();
	        tsstack.push(ts);
            //add time series and style
	        chart.addTimeSeries(ts, device_styles[d]);
	}
	charts.push(chart);
    }
    chtl = charts.length;
});

function update_data() {
    $.getJSON('/api/data', function(jd){
        var cd = jd['current'];
        console.log(cd);
        for (var c = 0; c < chtl; c++){
            var dt = datatypes[c];
            chart = charts[c];	    
            for (var d = 0; d < devl; d++){
                var device = devices[d];
                ts = tsstack[c*devl+d];
                var devdat = cd[device];
                if (devdat == null){
                    console.log('No data from device!!!') // here must be warning notification
                } else {
                    ts.append(new Date().getTime(), devdat[dt]);
                }
            }
        }
    });
}

setInterval(update_data, delay);
