function DashboardViewModel() {		
	var self = this;

	self.LoadDashboard = function() {
		$.ajax({
			url: "/api/jms/dashboard",
			success: function(dashboard) {
			
			},
			error: function() {
		
			}
		});
	}
}

var dashboard = new DashboardViewModel();
ko.applyBindings(dashboard, document.getElementById("dashboard"));
