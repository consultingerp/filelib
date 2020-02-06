$(document).ready(function() {

	$.post('/hhjc_install_cost_data',{
	},function(datas) {
		var d = JSON.parse(datas);
		$('#company_id_dom').text(d.name);
		$('#remark_dom').html(d.remark);
		for(var i=0;i<d.lines.length;i++){
			line = d.lines[i];
			var tr = "<tr>" +
					"<td>"+line.name+"</td>" +
					"<td>"+line.install_cost+"</td>" +
					"<td>"+line.uninstall_cost+"</td>" +
					"</tr>";

			$('#line_dom').append(tr);
		}
	});
});