var map = L.map('map');

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

/*L.tileLayer.provider('MapBox', {
    id: 'mapbox.satellite',
    accessToken: 'pk.eyJ1IjoibWFyY28tZGlzdHJ1dHRpIiwiYSI6ImNrNm9mc3E2eDBldjQzcm05d3lndDIzM3QifQ.XMxAYzSIzCVLSySDdCwa_w'
}).addTo(map);*/

var waypointsRaw = [{"serial": -1, "coords": [45.5069182, 9.2684501]}, {"serial": "219011040", "coords": [45.47681135126372, 9.236512472567256]}, {"serial": "5018009659", "coords": [45.4762310952844, 9.236555431203897]}, {"serial": "5018009646", "coords": [45.477248986363364, 9.234552703418103]}, {"serial": "219011021", "coords": [45.47857617193017, 9.234735671658427]}, {"serial": "4318007707", "coords": [45.474368278232184, 9.234338967171198]}, {"serial": "4318007515", "coords": [45.47432543032346, 9.232320695256137]}, {"serial": "4318007516", "coords": [45.47349815273121, 9.229721747711892]}, {"serial": "4318007559", "coords": [45.47348419239968, 9.227988218565317]}, {"serial": "4318007524", "coords": [45.47339194821373, 9.227660576438666]}, {"serial": "4318007369", "coords": [45.47394513204917, 9.227421338381987]}, {"serial": "5018010117", "coords": [45.47324078822479, 9.226786487398158]}, {"serial": "4318007593", "coords": [45.472509993695795, 9.225863839969406]}, {"serial": "4318007392", "coords": [45.47087005793701, 9.226536854525989]}, {"serial": "4318007565", "coords": [45.46989426546558, 9.225974704326633]}, {"serial": "4318007718", "coords": [45.46983965978507, 9.226052817146636]}, {"serial": "4318007571", "coords": [45.46979989609042, 9.227294493115664]}, {"serial": "4318007531", "coords": [45.470390857594786, 9.227506837512694]}, {"serial": "5018009656", "coords": [45.470878000000006, 9.2300566]}, {"serial": "5018009648", "coords": [45.4700976, 9.230013699999999]}, {"serial": "5018009643", "coords": [45.4712436, 9.230196699999999]}, {"serial": "219010944", "coords": [45.471815509081146, 9.232390411822394]}, {"serial": "5018009631", "coords": [45.4710123, 9.2336445]}, {"serial": "5018009615", "coords": [45.4709396, 9.230516]}, {"serial": "5018009654", "coords": [45.470962799999995, 9.2301679]}, {"serial": "5018009647", "coords": [45.4709595, 9.2299969]}, {"serial": "219011037", "coords": [45.47296783344937, 9.230443332167622]}, {"serial": "119010277", "coords": [45.473435525074905, 9.230480336576989]}, {"serial": "219011016", "coords": [45.4764079, 9.2301865]}, {"serial": "4318007701", "coords": [45.47690599389306, 9.230556221773213]}, {"serial": "4318007703", "coords": [45.47689494494104, 9.23231118664853]}, {"serial": "4318007695", "coords": [45.47583243405094, 9.234297548367293]}, {"serial": "5018009655", "coords": [45.4726973, 9.234613000000001]}, {"serial": "5018009661", "coords": [45.4709253, 9.239101300000002]}, {"serial": "5018009657", "coords": [45.47092070000001, 9.2376658]}, {"serial": "5018009620", "coords": [45.4710307, 9.2362065]}, {"serial": "219011029", "coords": [45.46973551950307, 9.23505322036192]}, {"serial": "4318007587", "coords": [45.46929703798276, 9.235052561902306]}, {"serial": "4318007739", "coords": [45.46850491031658, 9.232255184295813]}, {"serial": "4318007379", "coords": [45.468454773015296, 9.230469632182917]}, {"serial": "4318007393", "coords": [45.46848033635006, 9.229371560632103]}, {"serial": "5018009650", "coords": [45.4692007, 9.2302654]}, {"serial": "4318007665", "coords": [45.4680907, 9.2302748]}, {"serial": "4318007366", "coords": [45.467697912276314, 9.227228319795243]}, {"serial": "4318007404", "coords": [45.46774962908058, 9.231043369988127]}, {"serial": "2818001590", "coords": [45.4678075036686, 9.232572161250461]}, {"serial": "2818001955", "coords": [45.46793544831709, 9.232968129952496]}, {"serial": "4318007370", "coords": [45.46809901366692, 9.232957817505168]}, {"serial": "4318007385", "coords": [45.469387426059065, 9.236073335101537]}, {"serial": "4118006927", "coords": [45.47224514287364, 9.241329910054104]}, {"serial": -1, "coords": [45.5069182, 9.2684501]}];
L.tileLayer.provider('Hydda.Full')
var waypoints = []
var counter = 0

var url = new URL(location.href)
var step = url.searchParams.get("step")

for(var i = 0; i < waypointsRaw.length; i++){
	var coords = waypointsRaw[i].coords;
	waypoints.push(L.latLng(coords[0],coords[1]))
}

var control = L.Routing.control(L.extend(window.lrmConfig, {
	waypoints: waypoints,
	geocoder: L.Control.Geocoder.nominatim(),
	routeWhileDragging: true,
	reverseWaypoints: true,
	/*showAlternatives: true,*/
	altLineOptions: {
		styles: [
			{color: 'black', opacity: 0.15, weight: 9},
			{color: 'white', opacity: 0.8, weight: 6},
			{color: 'blue', opacity: 0.5, weight: 2}
		]
	},
	serviceUrl: 'http://localhost:5000/route/v1'
})).addTo(map);

L.Routing.errorControl(control).addTo(map);