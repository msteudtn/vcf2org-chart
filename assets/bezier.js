// Function to draw Bezier curves based on one start-point and multiple end-points
function drawBezier(startID, endIDs)
{

	// Check if a starting point was given. If not, quit.
	if (typeof(startID) !== "undefined") 
	{
		
		// Remove any existing SVG (path and circles)
		removeBezier()
		
		// 1b. Open all contact-levels, because some targets might still be hidden (CSS "display:none" -> X,Y position = 0,0)
		// toggle_levels(99)

		// 1c. Elevate the variables to a GLOBAL context, so we can use them again.
		window.startID = startID
		window.endIDs = endIDs

		// Create an array out of the string for "endIDs"
		// Example: "p1,p2,p99" -> ["p1", "p2", "p99"]
		array_endIDs = endIDs.split(",")
			
		// 2a. Create a name-space element (NS) "SVG"
		var svg_svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
		svg_svg.setAttribute("id", "svg")
		
		// 2b. Append the SVG to the BODY. The path and circles will be added later.
		document.body.appendChild(svg_svg)
		
		// 3. Loop through the end-IDs 
		for (i = 0; i <= array_endIDs.length-1; i++)
		{
			
			// 4. Get the HTML object based on its ID.
			var div1ID = startID
			var div2ID = "p"+array_endIDs[i] // Correct the endIDs from "13,37,99" to "p13,p37,p99"

			open_all_parents_of_id(div2ID)

			var div1 = document.getElementById(div1ID);
			var div2 = document.getElementById(div2ID);
			
			// Get the center-bottom coordinates of the DIVs - even if it outside of the viewport ("getBoundingClientRect")
			var x1 = div1.getBoundingClientRect().left + (div1.getBoundingClientRect().width /2);
			var y1 = div1.getBoundingClientRect().top + (div1.getBoundingClientRect().height /1);
			var x2 = div2.getBoundingClientRect().left + (div2.getBoundingClientRect().width /2);
			var y2 = div2.getBoundingClientRect().top + (div2.getBoundingClientRect().height /1);
			

			// 5a. Create a name-space element (NS) SVG-PATH
			var svg_path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
			
			// Create an ID for the path based on the DIV-names, so we can delete any existing paths in case of a resize / change / scroll.
			// svg_path.setAttribute("id", "path"+div1ID+"_"+div2ID)
			
			// Set the coordinates for start (x1, y1), bezier-point (window width and -height), and end-point (x2, y2)
			svg_path.setAttribute('d', "M "+x1+" "+y1+" Q "+(window.innerWidth/2)+" "+(window.innerHeight/1)+" "+x2+" "+y2+"")
			
			// Set colors and width 
			svg_path.setAttribute("stroke", "red")
			svg_path.setAttribute("stroke-width", "3")
			svg_path.setAttribute("fill", "none")

			// append the PATH to the SVG
			svg_svg.appendChild(svg_path)

			// 5b. Create a name-space element (NS) SVG-G (group)
			var svg_g = document.createElementNS('http://www.w3.org/2000/svg', 'g')

			// 5c. Create a name-space element (NS) SVG-CIRCLE
			var svg_circle1 = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
			var svg_circle2 = document.createElementNS('http://www.w3.org/2000/svg', 'circle')

			// Set radius, position, colors and width 
			svg_circle1.setAttribute('cx', x1)
			svg_circle1.setAttribute('cy', y1)
			svg_circle1.setAttribute('r', 8)
			svg_circle1.setAttribute('fill', "red")
			svg_circle1.setAttribute('stroke', "black")
			svg_circle1.setAttribute('stroke-width', "1")

			svg_circle2.setAttribute('cx', x2)
			svg_circle2.setAttribute('cy', y2)
			svg_circle2.setAttribute('r', 8)
			svg_circle2.setAttribute('fill', "white")
			svg_circle2.setAttribute('stroke', "red")
			svg_circle2.setAttribute('stroke-width', "2")

			// append the CIRCLES to the SVG-GROUP 
			svg_g.appendChild(svg_circle1)
			svg_g.appendChild(svg_circle2)

			// append the SVG-GROUP to the SVG
			svg_svg.appendChild(svg_g)
			
		} // end of: for() endIDs


		// Change the button icon and onclick()-function to "REMOVE"
		var toggle_button = "button_Connections_"+startID;

		var icon = ""
		icon += "&nbsp;&#x238C;"; // Icon: undo action
//		icon += "<sub>"+array_endIDs.length;+"</sub>"
		icon += "<sub>"+document.getElementById(toggle_button).dataset.number;+"</sub>"

		document.getElementById(toggle_button).innerHTML  = icon
		document.getElementById(toggle_button).setAttribute("onclick", "removeBezier(1,'"+startID+"', '"+endIDs+"')")

	}
	else
	{
		// nothing to do. No starting point giving or unset.	
	} // end of: if-else startID

}


// Remove any existing SVG (path and circles) 
// a) in case of resize / change / scroll. -> Keep variables -> drawBezier() with new coordinates
// b) on demand -> Unset variables -> Can't draw a new SVG
function removeBezier(bool_requested, startID, endIDs) 
{
	// The connection lines will always be shown, as long as the global variables "startID" and "endIDs" exist
	// To turn it off, we delete the variables on request
	if (bool_requested)
	{
		// Change the button icon and onclick()-function to "DRAW"
		var toggle_button = "button_Connections_"+startID;

		var icon = ""
		icon += "&nbsp;&#x260B;"; // Icon:  descending node
//		icon += "<sub>"+array_endIDs.length;+"</sub>"
		icon += "<sub>"+document.getElementById(toggle_button).dataset.number;+"</sub>"

		document.getElementById(toggle_button).innerHTML  = icon
		document.getElementById(toggle_button).setAttribute("onclick", "drawBezier('"+startID+"', '"+endIDs+"')")

		// Unset variables
		startID = undefined
		endIDs = undefined

		// Elevate the variables to a GLOBAL context, so other functions know, they're unset.
		window.startID = startID
		window.endIDs = endIDs
	}
	else
	{
		// Nothing to do. The variables will be kept.
	}

	// Completely remove / delete the SVG with paths and circles.
	try {
		document.getElementById("svg").remove()		
		}
	catch (error) {}
}


// Check, if the window has changed and try to call the function - IF we already have some IDs.
document.addEventListener("scroll", (event) => { 
	try 
	{
		drawBezier(startID, endIDs)
	}
	catch {}
})
