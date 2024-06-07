$("#warning_textbox").css("visibility", "visible");
$("#currentTime").css("color", "white");
var typ = '正式接口呐';
document.getElementById("warning_textbox").innerHTML = typ;

var drawseis = false;

//定义烈度配色
const intColor = {
    "0": {
        "bkcolor": "#2e2e2e"
    },
    "1": {
        "bkcolor": "#9edeff"
    },
    "2": {
        "bkcolor": "#76cbf6"
    },
    "3": {
        "bkcolor": "#3cbdff"
    },
    "4": {
        "bkcolor": "#46BC67"
    },
    "5": {
        "bkcolor": "#12994E"
    },
    "6": {
        "bkcolor": "#F6B72D"
    },
    "7": {
        "bkcolor": "#FF8400"
    },
    "8": {
        "bkcolor": "#fa5151"
    },
    "9": {
        "bkcolor": "#f4440d"
    },
    "10": {
        "bkcolor": "#ff000d"
    },
    "11": {
        "bkcolor": "#c20007"
    },
    "12": {
        "bkcolor": "#fd2fc2"
    }
};

var ding = new Audio('static/audio/countdown/ding.mp3');
var sixty = new Audio('static/audio/countdown/60.mp3');
var fifty = new Audio('static/audio/countdown/50.mp3');
var forty = new Audio('static/audio/countdown/40.mp3');
var thirsty = new Audio('static/audio/countdown/30.mp3');
var twenty = new Audio('static/audio/countdown/20.mp3');
var ten = new Audio('static/audio/countdown/10.mp3');
var nine = new Audio('static/audio/countdown/9.mp3');
var eight = new Audio('static/audio/countdown/8.mp3');
var seven = new Audio('static/audio/countdown/7.mp3');
var six = new Audio('static/audio/countdown/6.mp3');
var five = new Audio('static/audio/countdown/5.mp3');
var four = new Audio('static/audio/countdown/4.mp3');
var three = new Audio('static/audio/countdown/3.mp3');
var two = new Audio('static/audio/countdown/2.mp3');
var one = new Audio('static/audio/countdown/1.mp3');
var arrive = new Audio('static/audio/countdown/arrive.mp3');

var map = new BMapGL.Map("allmap");
map.setMapStyleV2({
    styleId: 'ccff97869e9448f19f822123114357ae'
});
var scaleCtrl = new BMapGL.ScaleControl();  // 添加比例尺控件
map.addControl(scaleCtrl);
map.enableScrollWheelZoom(true);
var _open = true;


/*window.addEventListener("load", function () {
    setTimeout(function () {
        $("#loading_Background").fadeTo("slow", 0);
    }, 1000);*/
setTimeout(function () {
    $("#loading_Background").css("height", "0px");
    $("#loading_Background").css("width", "0px");
}, 2000)
//});

function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");

    if (arr = document.cookie.match(reg)) return unescape(arr[2]);
    else return null;
}

document.getElementById("myBtn").addEventListener("click", function () {
    $("#1").css("visibility", "visible");
    $("#2").css("visibility", "visible");
    $("#myBtn3").css("visibility", "visible");
    $("#myBtn4").css("visibility", "visible");
    $("#form-control-text").css("visibility", "hidden");
    $("#form-control-text2").css("visibility", "hidden");

});
document.getElementById("myBtn4").addEventListener("click", function () {
    $("#1").css("visibility", "hidden");
    $("#2").css("visibility", "hidden");
    $("#myBtn3").css("visibility", "hidden");
    $("#myBtn4").css("visibility", "hidden");
    $("#form-control-text").css("visibility", "visible");
    $("#form-control-text2").css("visibility", "visible");

});
document.getElementById("myBtn3").addEventListener("click", function () {
    if (isNaN(Number(document.getElementById("2").value)) || isNaN(Number(document.getElementById("1").value)) || document.getElementById("1").value < 0 || document.getElementById("1").value > 180 || document.getElementById("2").value > 90 || document.getElementById("2").value < 0 || document.getElementById("1").value == "" || document.getElementById("2").value == "") {
        alert("输入不合规，请重新输入（仅支持东北半球，请勿输入英文）");
    }
    else {
        var oDate = new Date();
        oDate.setDate(oDate.getDate() + 30);
        document.cookie = "la=" + document.getElementById("2").value + ";" + "expires=" + oDate;
        document.cookie = "ln=" + document.getElementById("1").value + ";" + "expires=" + oDate;
        console.log("success");
        window.location.href = '/';
    }
});

document.getElementById("myBtn2").addEventListener("click", function () {
    backcenter();
});

document.getElementById("myBtn7").addEventListener("click", function () {
    window.location.href = 'https://uews.rainyangty.top';
});

document.ontouchmove = function (e) {
    e.preventDefault();
}

var systemTime;
var systemTimeStamp;
var currentTimeStamp;
var update = false;
var shake = false;
var centerIcon = new BMapGL.Icon("static/epicenter.png", new BMapGL.Size(50, 50));
var seisIcon = new BMapGL.Icon("static/seis.png", new BMapGL.Size(10, 10));

var sc_eewStartAt;
var sc_eewLat;
var sc_eewLon;
var sc_eewDepth;
var sc_eewMagnitude;
var sc_eewEpicenter;
var sc_eewlastId;
var sc_eewUpdates;
var sc_eewmainMaxInt;
var sc_eewlocalname;
var sc_eewarrivetime;

var localLat = getCookie("la");
var localLon = getCookie("ln");
var minInt = 0.0;
if (localLat == null)
    _open = false
else
{
    document.getElementById("form-control-text").innerHTML = getCookie("ln") + "°E";
    document.getElementById("form-control-text2").innerHTML = getCookie("la") + "°N";
}
var deltatime = 0;

function backcenter() {
    var point = new BMapGL.Point(103.79942839007867, 36.093496518166944);
    //var centerpoint = new BMapGL.Marker(point, { icon: centerIcon });
    //map.addOverlay(centerpoint)
    map.centerAndZoom(new BMapGL.Point(103.79942839007867, 36.093496518166944), 5);
}

window.onresize = function() {
    setTimeout(function () {
        backcenter();
    }, 100);
};  

//计算sub最大烈度
function calcMaxInt(calcMagnitude, calcDepth) {
    let numa = 1.65 * calcMagnitude;
    let numb = calcDepth < 10 ? 1.21 * Math.log10(10) : 1.21 * Math.log10(calcDepth);
    let maxInt = Math.round(numa / numb) < 12 ? Math.round(numa / numb) : 12.0;
    return (maxInt);
}

function TimestampToDate(Timestamp) {
    let now = new Date(Timestamp),
        y = now.getFullYear(),
        m = now.getMonth() + 1,
        d = now.getDate();
    return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
}

function DateToTimestamp(_Date) {
    return new Date(_Date).getTime();
}

function getcurrenttime() //同步时间
{
    var start = Date.now();
    $.getJSON("https://api.wolfx.jp/ntp.json?" + Date.now(),
        function (json) {
            systemTime = Date();
            systemTimeStamp = Date.now();
            deltatime = DateToTimestamp(json.CST.str) - Date.parse(new Date()) + (systemTimeStamp - start);
            // console.log(deltatime)
            if (deltatime / 1000 >= 10) {
                $("#warning_textbox").css("visibility", "visible");
                $("#currentTime").css("color", "red");
                document.getElementById("warning_textbox").innerHTML = "请校准系统时间";
            }
            else {
                $("#warning_textbox").css("visibility", "hidden");
                $("#currentTime").css("color", "white");
                //document.getElementById("warning_textbox").innerHTML = "内部测试";
            }
        });
}

function settime() //同步时间
{
    systemTime = Date();
    systemTimeStamp = Date.now();
    currentTimeStamp = Date.parse(new Date()) + deltatime;
    document.getElementById("currentTime").innerHTML = TimestampToDate(Date.parse(new Date()) + deltatime);
}

var lasteventid = 0;
var sc_eewcancel = true;

var sceewsWave = new BMapGL.Circle(new BMapGL.Point(107.79942839007867, 37.093496518166944), 0, { strokeColor: "#FFA500", fillColor: "#FFA500", strokeWeight: 2, strokeOpacity: 0.5 }, "s"); //创建圆
var sceewpWave = new BMapGL.Circle(new BMapGL.Point(107.79942839007867, 37.093496518166944), (0 / 4 * 7), { strokeColor: "#00FFFF", fillColor: "#242424", strokeWeight: 2, strokeOpacity: 0.5 }, "s"); //创建圆
var delta = 0;
var warningtf = false;
function sceew()
{
    $.getJSON("/static/sc_eew.json?" + Date.now(),//https://api.wolfx.jp/sc_eew.json
        function (json) {
            sc_eewLat = json.Latitude;
            sc_eewLon = json.Longitude;
            sc_eewDepth = json.Depth;
            delta = json.Delta
            sc_eewStartAt = Date.parse(new Date(json.OriginTime).toString()) - delta * 1000;
            sc_eewUpdates = json.ReportNum;
            sc_eewEpicenter = json.HypoCenter;
            sc_eewMagnitude = json.Magunitude;
            sc_eewlocalname = json.HypoCenter;
            eventid = json.EventID;
            if (lasteventid != eventid)
            {
                lasteventid = eventid;
                var music = new Audio('static/audio/update.mp3');
                music.play();
            }
            

            sc_eewMaxInt = calcMaxInt(sc_eewMagnitude, sc_eewDepth);

            distance = _open ? getDistance(sc_eewLat, sc_eewLon, localLat, localLon) : 0;
            sc_eewarrivetime = Math.round(distance / 4) + delta;
            if ((currentTimeStamp - sc_eewStartAt) / 1000 <= 60 + sc_eewarrivetime && currentTimeStamp - sc_eewStartAt >= 0) {
                sc_eewcancel = false;
                $("#currentTime").css("color", "red");
                $("#textbox").css("background-color", "red");
                // countDown(sc_eewLat, sc_eewLon, sc_eewStartAt, sc_eewMagnitude, sc_eewMaxInt, sc_eewlocalname);
                $("#eewmainBar").css("visibility", "visible");
                document.getElementById("textbox").innerHTML = "架空模拟 第" + sc_eewUpdates + "报";
                $("#eewmainBar2").css("visibility", "hidden");
                document.getElementById("eewmainTime").innerHTML = TimestampToDate(sc_eewStartAt);
                document.getElementById("eewmainEpicenter").innerHTML = sc_eewLat + "°N " + sc_eewLon + "°E";
                if (sc_eewDepth != null)
                    document.getElementById("eewmainDepth").innerHTML = sc_eewDepth + "km";
                else
                    document.getElementById("eewmainDepth").innerHTML = "深度未知";
                document.getElementById("eewmainMagnitude").innerHTML = '<font size="4">M</font>' + (Math.round(sc_eewMagnitude * 100) / 100);
                $("#eewmainMaxInt").css("background-color", intColor[sc_eewMaxInt].bkcolor);
                document.getElementById("eewmainMaxInt").innerHTML = sc_eewMaxInt;
            
                //map.centerAndZoom(new BMapGL.Point(eewLon, eewLat), 12);
                var point = new BMapGL.Point(sc_eewLon, sc_eewLat);
                var centerpoint = new BMapGL.Marker(point, { icon: centerIcon });
                sceewsWave.setCenter(point);
                sceewpWave.setCenter(point);
                map.addOverlay(centerpoint);
                map.disableScrollWheelZoom();
                map.disableDragging();
                //setInterval(drawwave, 0.01, eewLon, eewLat, eewStartAt, "eew");
            }
            else if (!sc_eewcancel) {
                map.enableScrollWheelZoom();
                map.enableDragging();
                sceewsWave.setRadius(0);
                sceewpWave.setRadius(0 / 4 * 7);
                document.getElementById("textbox").innerHTML = "当前无生效中的地震模拟";
                backcenter();
                sc_eewcancel = true;
                $("#currentTime").css("color", "white");
                $("#textbox").css("background-color", "#3b3b3b");
                $("#eewmainBar").css("visibility", "hidden");
                $("#countDown").css("visibility", "hidden");
                //map.removeOverlay(sWave);
                //map.removeOverlay(pWave);
                map.clearOverlays();
                drawseis = false;
                var point = new BMapGL.Point(localLon, localLat);
                var marker = new BMapGL.Marker(point);        // 创建标注   
                map.addOverlay(marker);                     // 将标注添加到地图中
                warningtf = false;
                //window.location.href = 'index.html';
            }
        });
}

function _switch () {
    $.getJSON("/static/switch.json?" + Date.now(),
        function (json) {
            if(json.o == 0)
            {
                $("#myBtn6").css("visibility", "hidden");
            }
            else {
                $("#myBtn6").css("visibility", "visible");
            }
        });
}

var lastjson = ""
function updateLog()
{
    $.getJSON("/static/log.json?" + Date.now(),
        function (json) {
            if (json != lastjson)
            {
                document.getElementById("Logbox").scrollTop = document.getElementById("Logbox").scrollHeight;
                document.getElementById("Logbox").innerHTML = json.LOG
                lastjson = json
            }
        });
}
seisinfo = ""
function markseis()
{
    $.getJSON("/static/seis.json?" + Date.now(),
        function (json) {
            if (json != seisinfo && !sc_eewcancel)
            {
                var point = new BMapGL.Point(json.Lon, json.Lat);
                var seispoint = new BMapGL.Marker(point, { icon: seisIcon });
                map.addOverlay(seispoint);
            }
        });
}

function azooms() {
    //var view = map.getViewport(eval(sceewpWave));
    //var mapZoom = view.zoom;
    var mapZoom = 8
    map.centerAndZoom(new BMapGL.Point(sc_eewLon, sc_eewLat), mapZoom - 1);
}

function drawwave() {
    if ((Date.now() - sc_eewStartAt) / 1000 <= sc_eewarrivetime + 60 && !sc_eewcancel) {
        var sle = (Date.now() - sc_eewStartAt) * 4.0;
        sceewsWave.setRadius(sle);
        sceewpWave.setRadius(sle / 4.0 * 7.0);
        map.addOverlay(sceewpWave);
        map.addOverlay(sceewsWave);
        azooms();
    }
}

function getDistance(lat1, lng1, lat2, lng2) {
    var radLat1 = lat1 * Math.PI / 180.0;
    var radLat2 = lat2 * Math.PI / 180.0;
    var a = radLat1 - radLat2;
    var b = lng1 * Math.PI / 180.0 - lng2 * Math.PI / 180.0;
    var s = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(a / 2), 2) +
        Math.cos(radLat1) * Math.cos(radLat2) * Math.pow(Math.sin(b / 2), 2)));
    s = s * 6378.137;
    s = Math.round(s * 10000) / 10000;
    return s  // 单位千米
}

var localInt;
var feel;
var distance;
function countDown() {
    var Lat, Lon, StartAt, arrivetime, MaxInt, Epicenter, cancel;
    Lat = sc_eewLat;
    Lon = sc_eewLon;
    StartAt = sc_eewStartAt;
    arrivetime = sc_eewarrivetime;
    MaxInt = sc_eewmainMaxInt;
    Epicenter = sc_eewEpicenter;
    cancel = sc_eewcancel;
    Magnitude = sc_eewMagnitude;
    distance = getDistance(Lat, Lon, localLat, localLon);
    timeMinus = currentTimeStamp - StartAt;
    timeMinusSec = timeMinus / 1000;
    localInt = 0.92 + 1.63 * Magnitude - 3.49 * Math.log10(distance);

    if (timeMinus <= 60000 * 60 + arrivetime * 60000 && _open && !cancel) {//&& localInt >= minInt
        $("#countDown").css("visibility", "visible");
        if (!warningtf) {
            warningtf = true;
            var music = new Audio('static/audio/eew1.mp3');
            music.play();
        }
        if (localInt < 0) {
            localInt = "0.0"
        } else if (localInt >= 0 && localInt < 12) {
            localInt = localInt.toFixed(1);
        } else if (localInt >= 12) {
            localInt = "12.0"
        }
        if (localInt >= MaxInt) localInt = MaxInt;
        if (localInt < 1.0) {
            feel = "无震感";
        } else if (localInt >= 1.0 && localInt < 2.0) {
            feel = "震感微弱";
        } else if (localInt >= 2.0 && localInt < 3.0) {
            feel = "高楼层有震感";
        } else if (localInt >= 3.0 && localInt < 4.0) {
            feel = "震感较强";
        } else if (localInt >= 4.0 && localInt < 5.0) {
            feel = "震感强烈";
        } else if (localInt >= 5.0) {
            feel = "震感极强";
        }
        $("#eewMaxInt").css("background-color", intColor[Math.round(localInt) <= 0 ? 0 : Math.round(localInt)].bkcolor);
        document.getElementById("eewMaxInt").innerHTML = Math.round(localInt) <= 0 ? 0 : Math.round(localInt);
    }
}

var cd = 0;
var cdp = 0;

function countdownAudio() {
    if (warningtf && localInt >= 3.0) {
        if (cd == 61) {
            sixty.play();
        }
        else if (cd == 51) {
            fifty.play();
        }
        else if (cd == 41) {
            forty.play();
        }
        else if (cd == 31) {
            thirsty.play();
        }
        else if (cd == 21) {
            twenty.play();
        }
        else if (cd == 11) {
            ten.play();
        }
        else if (cd == 10) {
            nine.play();
        }
        else if (cd == 9) {
            eight.play();
        }
        else if (cd == 8) {
            seven.play();
        }
        else if (cd == 7) {
            six.play();
        }
        else if (cd == 6) {
            five.play();
        }
        else if (cd == 5) {
            four.play();
        }
        else if (cd == 4) {
            three.play();
        }
        else if (cd == 3) {
            two.play();
        }
        else if (cd == 2) {
            one.play();
        }
        else if (cd == 1) {
            arrive.play();
        }
        else {
            ding.play();
        }
    }
}

function countdownRun() {
    if (!_open) {
        return;
    }
    else if ((Date.now() - sc_eewStartAt) / 1000 <= sc_eewarrivetime) {
        distance = getDistance(sc_eewLat, sc_eewLon, localLat, localLon);
        timeMinus = Date.now() - sc_eewStartAt;
        timeMinusSec = timeMinus / 1000;
        cd = Math.round(distance / 4 - timeMinusSec);
        cdp = Math.round(distance / 7 - timeMinusSec);
        if (cd <= 0) {
            cd = "抵达";
            //document.getElementById("countDown_Text").innerHTML = feel + "<br>" + "地震横波已抵达";
        }
        if (cdp <= 0) {
            cdp = "抵达";
            //document.getElementById("countDown_Text").innerHTML = feel + "<br>" + "地震横波已抵达";
        }
        else {
            //document.getElementById("countDown_Text").innerHTML = feel + "<br>" + "地震横波将抵达";
        }
        if (cd >= 999) cd = 999;
        if (cdp >= 999) cdp = 999;
        document.getElementById("countDown_SNumber").innerHTML = cd;
        document.getElementById("countDown_PNumber").innerHTML = cdp;
    }
    else {
        cd = "抵达";
        cdp = "抵达";
        //document.getElementById("countDown_Text").innerHTML = feel + "<br>" + "地震横波已抵达";
        document.getElementById("countDown_SNumber").innerHTML = cd;
        document.getElementById("countDown_PNumber").innerHTML = cdp;
    }
    //console.log("countdownRun() 运行中");
}

backcenter();
setInterval(drawwave, 100);
setInterval(updateLog, 500);
setInterval(settime, 500);
setInterval(sceew, 500);
setInterval(countdownAudio, 1000);
setInterval(countdownRun, 1000);
setInterval(countDown, 1000);
setInterval(getcurrenttime, 10000);
setInterval(_switch, 1000);
setInterval(markseis, 100);
$("#currentTime").css("color", "white");