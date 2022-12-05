/**
it basically just doesn't work
just get browser blocking due to cors etc.  I just can't get aroudn it, any way seems very complex
So I would go back to plan A
1) serve the static pages from lambda, like I did before, just put all into an html page or maybe send as objects in a json string
2) do as I was planning to do with lambda to return dynamic content
This gets aroun the cors problem
I think you have to use cloudfront to avoid the cors issue, so it basically gives you one domain and then routes requests to either S3 for static or lambda for dynamic


So rebuild the lmabda only verison

 */




//this is global code
//#################################################################################
let gp = {
	ind : 0,
	max_offset : 180,
	min_offset : -216,
	t_now : Date.now(),
	swipe_timeout : 50,   //ms
	fetch_url : 'https://o15b9h47ik.execute-api.ap-southeast-2.amazonaws.com/test/fetch',    //shold be able to get this from the DOM!?!?
	img : {},
	pw : "DfThGfDjNv4D3F67YtgB98HGb",
};
//add ind_s
gp.ind_s = ind2str(gp.ind);





function ind2str(x) {
	let y = x.toString();
	if (y == '0') {
		y = '00'
	}
	return y
}






function display_images(offset) {
	let prefix = "data:image/png;base64,";

	let el = document.getElementById("slp");
	let data = gp.img[offset][0];
	el.src = `${prefix}${data}`;
	el = document.getElementById("swell");
	data = gp.img[offset][1];
	el.src = `${prefix}${data}`;
	el = document.getElementById("period");
	data = gp.img[offset][2];
	el.src = `${prefix}${data}`;
	el = document.getElementById("wave");
	data = gp.img[offset][3];
	el.src = `${prefix}${data}`;
}







function ajax_post(url, data, headers, display=true) {
	$.ajax({
		type: "POST",
		//type: "GET",
		url: url,
		crossDomain: true,
		contentType: 'application/json',
		headers: headers,
		data: data,
		success: function(response){ 
			let cnt = 0;
			for (let key of Object.keys(response)) {
				//key will be string
				cnt += 1;
				gp.img[key] = response[key];
				if (display && cnt == 1) {
					display_images(key);
					$("#status").text(`time offset: ${key} hrs`);
				}
			}
		},
		error: function () {
			alert("error occurred while getting data");
		}
	});
}





function get_data(offset, display=true) {
	/**
	 * this is getting images as b64 and storing them in the img object
	 * 
	 */
	$("#status").text("updating images...")
	if (Object.hasOwn(gp.img, offset)) {
		//get the data from the img object, we already have it locally
		if (display) {
			display_images(offset);
			$("#status").text(`time offset: ${offset} hrs`);
		}
	}
	else {
		//get it from the server
		let fetch_data = {"offsets": [offset]};
		ajax_post(
			url = gp.fetch_url, 
			data = JSON.stringify(fetch_data), 
			headers = {"pw": gp.pw}, 
			display = true
		);
	}		
}







function get_data_bulk(offsets, refresh=false) {
	$("#status").text("updating images...")
	//just get the images of the list of offsets from the server
	let offsets_to_get = [];
	if (refresh == false) {
		for (let i = 0; i < offsets.length; i++) {
			if (!Object.hasOwn(gp.img, offsets[i])) {
				offsets_to_get.push(offsets[i]);
			}
		}  
	}
	else {
		offsets_to_get = offsets;
	}

	//only do ajax if we have offsets to get
	if (offsets_to_get.length > 0) {
		let fetch_data = {'offsets': offsets_to_get};
		ajax_post(
			url = gp.fetch_url, 
			data = JSON.stringify(fetch_data), 
			headers = {"pw": gp.pw}, 
			display = false
		);
	}
}





function step_backward() {
	gp.ind = Math.max(gp.ind - 6, gp.min_offset);
	gp.ind_s = ind2str(gp.ind);
	get_data(gp.ind_s);
}




function step_forward() {
	gp.ind = Math.min(gp.ind + 6, gp.max_offset);
	gp.ind_s = ind2str(gp.ind);
	get_data(gp.ind_s);
}


  
function get_all_steps(refresh=true) {
	//get all slices, as it is a big download, get them slice by slice
	let offsets = [];
	for (let i = gp.min_offset; i <= gp.max_offset; i += 6) {
		offsets.push(ind2str(i));
	}  
	let chunkSize = 4;  //offsets
	let cnt = 0;
	for (let i = 0; i < offsets.length; i += chunkSize) {
		const chunk = offsets.slice(i, i + chunkSize);
		//$("#status").text(`getting chunk: ${cnt} of ${parseInt(offsets/chunkSize)}`);
		get_data_bulk(chunk, refresh);
	}
	//$("#status").text("Done");
}







function add_listeners() {
	//add listeners to the back and next buttons
	$("#next_button").on("click", function() {
		step_forward();
	});

	$("#back_button").on("click", function() {
		step_backward();
	});

	$("#all_button").on("click", function() {
		get_all_steps(false);
	});

	$("#refresh_button").on("click", function() {
		get_all_steps(true);
	});

	//add the back/next listener to the left/right arrow keys also
	window.addEventListener("keydown", (event) => {
		if (event.defaultPrevented) {
			return; // Do nothing if the event was already processed
		}
		switch (event.key) {
			case "ArrowLeft":
				step_backward();
				break;
			case "ArrowRight":
				step_forward();
				break;
		  	default:
				return; // Quit when this doesn't handle the key event.
		}
		event.preventDefault();    // Cancel the default action to avoid it being handled twice
	}, true);

	
	//add swipe left/right listeners
	$("*").on("swiperight", function(e) {
		let t = Date.now();
		if (t - gp.t_now > gp.swipe_timeout) {    // need this otherwise it seems to send ~10 events in very quick succession for one swipe
			//x coords are in e.swipestart.coords[0] and e.swipestop.coords[0] in pixels
			gp.t_now = t; 
			step_backward();
		}
	});

	$("*").on("swipeleft", function(e) {
		let t = Date.now();
		if (t - gp.t_now > gp.swipe_timeout) {    // need this otherwise it seems to send ~10 events in very quick succession for one swipe
			//x coords are in e.swipestart.coords[0] and e.swipestop.coords[0] in pixels, but they will only be for the last of the 10 rapid fire events, so will aways be ~20 pixels
			gp.t_now = t;
			step_forward();
		}
	});
}


function collapse_all(){
	//code to handle the collapse all function
	let x = document.getElementsByClassName("multicollapse");
	for (let i = 0 ; i < x.length; i++){
		if (x[i].classList.contains("show")){
			x[i].classList.remove("show");
		}
	}
}


function expand_all(){
	//code to handle the expand all function
	let x = document.getElementsByClassName("multicollapse");
	for (let i = 0; i < x.length; i++){
		if (!x[i].classList.contains("show")){
			x[i].classList.add("show");
		}
	}
}



//This code is specific to pinky's surf data page
$(document).ready(function() {
	//this limits this function to a particular html page, I'm allowing .../Pinky_vXXX.html
	//pattern = /\/index\.html/i;
	pattern = /.*/i;
	if (window.location.pathname.search(pattern) != -1) {
		//#################################################################################
		//set the initial images
		get_data(gp.ind_s, display=true)
		//add listeners to the back and next buttons
		add_listeners();
		//expand the multicollapse section		
		expand_all();

		//get rid of this weird thing one of the libs puts at the bottom of the page
		$("div.ui-loader").remove();
	
	}
})


