/*
(1.) Conversion of JSON to HTML list (<ol><li>) based on "treeData.js" by raphamorim
https://github.com/raphamorim/treeData.js
License: MIT
*/

'use strict';

// Set basic classes and IDs. Call the list-creation (buildTree()) and append it to the DOM.
function TreeData (data, select) {
	var main = document.querySelector(select);
	var treecanvas = document.createElement('ol');
	treecanvas.className = 'organizational-chart';
	treecanvas.id = 'contact-chart';

	var treeCode = buildTree(data, Object.keys(data)[0]);

	treecanvas.innerHTML = treeCode;

	// Append all the contacts as <ol><li> list
	main.appendChild(treecanvas);

	// Add a <select><option> box to show/hide the different levels of contacts
	build_select_form_for_levels();

	// Hide all levels below three by default
	toggle_levels(3)
}


// create the list (<ol><li>) based on the JSON and return.
function buildTree (obj, node) 
{
	var sons = [];
	var tabindex_counter = 0

	for (var i in obj) 
	{
		if (obj[i].parent == node)
		sons.push(i);

	}

	var treeString = "";
	var treeString_name = "";
	var treeString_photo = "";
	var treeString_details = "";
	var treeString_button_details = "";
	var treeString_button_children = "";
	var treeString_button_connections = ""


	// Start <LI> and <DIV> and add an ID "p00", "p99", ...
	treeString += "<li>";
	treeString += " <div id='"+obj[node].id+"'>";
	// treeString += "  <details>";
	// treeString += "   <summary>";

	// Contact PHOTO from the JSON.photo
	if (obj[node].photo.length > 0)
	{
		treeString_photo += "     <img src="+obj[node].photo+" style='height:2.0em; float:left; border:1px solid black;' />"
	}
	else { }


	// Contact NAME from the JSON.value
	treeString_name += " " + obj[node].value + " "


	// Add a "button" to show the contact-DETAILS (TEL, NOTE, URL, ...) with ID "Details_p00", "Details_p99", ...
	// Call the function toggleElement(elementId, icon_style) -> ("Details_p00", "arrow")
	treeString_button_details += "    "
	treeString_button_details += " <span class='mybutton'  " 
	treeString_button_details += " tabindex='0' role='button' aria-pressed='false' "	// ARIA
	treeString_button_details += " id='button_Details_"+obj[node].id+"' "			// ID
	treeString_button_details += " onclick=\"toggleElement('Details_"+obj[node].id+"', 'arrow')\" "	// call function on click
	treeString_button_details += " title='Show / Hide contact-details.'>"			// title
	treeString_button_details += "&nbsp;&#x25C1;&nbsp;"					// Icon: arrow left
	treeString_button_details += "</span> ";


	// Add a "button" to the element to hide / show the <ol><li>-CHILDREN-elements with ID "ol_p00", "ol_p99", ...
	// Call the function toggleElement(elementId, icon_style) -> ("ol_p00", "folder")
	if (sons.length > 0) 
	{
		treeString_button_children += "   "
		treeString_button_children += " <span class='mybutton' "
		treeString_button_children += " tabindex='0' role='button' aria-pressed='false' "	// ARIA
		treeString_button_children += " id='button_ol_"+obj[node].id+"' " 			// ID
		treeString_button_children += " data-number='"+sons.length+"' "  			// Number of (first) children / sub-levels as DATA-tag
		treeString_button_children += " onclick=\"toggleElement('ol_"+obj[node].id+"', 'folder')\" " 	// call function on click
		treeString_button_children += " title='Show / Hide child-elements.' > "			// title
		treeString_button_children += "&nbsp;&#x1F5C0" 						// Icon: closed folder
		treeString_button_children += "<sub>"+sons.length+"</sub>"  				// Number of children / sub-levels as string
		treeString_button_children += "</span> ";
	}


	// Add a "button" to show CONNECTIONS between contacts ...
	// Call the function drawBezier(startID, endIDs) on click
	if (obj[node].connections.length  > 0) 
	{
		treeString_button_connections += "    "
		treeString_button_connections += " <span class='mybutton' " 
		treeString_button_connections += " tabindex='0' role='button' aria-pressed='false' "	// ARIA
		treeString_button_connections += " id='button_Connections_"+obj[node].id+"' "		// ID
		treeString_button_connections += " data-number='"+obj[node].connections.length+"' "  	// Number of contacts as DATA-tag
		treeString_button_connections += " onclick=\"drawBezier('"+obj[node].id+"' , '"+obj[node].connections+"')\" "	// call function on click
		treeString_button_connections += " title='Show / Hide "+obj[node].connections.length+" connections.'>"		// title
		treeString_button_connections += "&nbsp;&#x260B;" 					// Icon: descending node
		treeString_button_connections += "<sub>"+obj[node].connections.length+"</sub>"  	// Number of contacts as string

		treeString_button_connections += "</span> ";
	}


	// Content for the contact DETAILS (telephone, URL, notes, ...) from the JSON.details
	treeString_details += "   <span class='class_for_details' style='display:none' id='Details_"+obj[node].id+"'>"+obj[node].details+"</span>";

	// treeString += "   </summary> "
	// treeString += "  </details> ";

	// TABLE to fill with all the contents
	// We're using a table because positioning of elements is easier. :) 
	treeString += " <table>"

		// ROW for [PHOTO], [NAME], [BUTTON for details] and [BUTTON for children]
		treeString += "  <tr>"

			treeString += "   <td rowspan='2'>"
			treeString += treeString_photo
			treeString += "   </td>"

			treeString += "   <td rowspan='2' style='vertical-align: middle; text-align: center;'>"
			treeString += treeString_name
			treeString += "   </td>"

			treeString += "   <td  style='vertical-align: bottom;  text-align: right;'>"
			treeString += treeString_button_details
			treeString += "   </td>"

			treeString += "   <td  style='vertical-align: bottom;  text-align: left;'>"
			treeString += treeString_button_children
			treeString += "   </td>"

		treeString += "  </tr>"

		// ROW for [rowspan from PHOTO], [rowspan from NAME], [BUTTON for connections] and [nothing]
		treeString += "  <tr>"

			treeString += "   <td style='vertical-align: top; text-align: right;'>"
			treeString += treeString_button_connections
			treeString += "   </td>"


			treeString += "   <td  style='vertical-align: top; text-align: left;'>"
			treeString += "   </td>"

		treeString += "  </tr>"

	treeString += " </table>"

	treeString += treeString_details

	treeString +=  "</div>";


	// Create a new <ol>-element with ID "ol_p00", "ol_p99" for the children of the parent <li>.
	// Example: <li> "My Family" 
	//             <ol> <li> "Lisa" 
	//                <ol> <li> "Ralph" </li>
	//                  </li> </ol>
	//           </li>
	if (sons.length > 0) 
	{
		treeString += "<ol id='ol_"+obj[node].id+"'>";

		for (var i in sons) 
		{
		treeString += buildTree(obj, sons[i]);
		}
		treeString += "</ol>";
	}
	return treeString;

}
