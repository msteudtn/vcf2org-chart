/*
(1.) Conversion of JSON to HTML list (<ol><li>) based on "treeData.js" by raphamorim
https://github.com/raphamorim/treeData.js
License: MIT

(2.) Buttons and functions to show / hide the elements based on own work and internet-research. ;) 
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
//		console.log("i: "+i)

	}


	var treeString = "";
	treeString += "<li>";
	treeString += " <div id='"+obj[node].id+"'>";
	// treeString += "  <details>";
	// treeString += "   <summary>";

	if (obj[node].photo.length > 0)
		{
		console.log("photo bei "+obj[node].id +" - "+ obj[node].value+ " - "+obj[node].photo)
		treeString += "<img src="+obj[node].photo+" style='height:2.5em; float:left;' />"
		}
	else { }


	// contact name
	treeString += " " + obj[node].value + " "

	// Add a "button" to the element to hide / show the <ol><li>-children-elements with ID "olp00", "olp99", ...
	if (sons.length > 0) 
	{
		treeString += "   "
		treeString += " <span class='mybutton' "
		treeString += " tabindex='0' role='button' aria-pressed='false' "
		treeString += " id='buttonol"+obj[node].id+"' " 
		treeString += " onclick=\"toggleElement('ol"+obj[node].id+"', 'folder')\" " 
		treeString += " title='Show / Hide child-elements.' > "
		treeString += "&nbsp;&#x1F5C0;&nbsp;"
		treeString += "</span> ";
	}
	// treeString += "   </summary> "

	// Add a "button" to show the contact-details (TEL, NOTE, URL, ...) with ID "Detailsp00", "Detailsp99", ...
	treeString += "    "
	treeString += " <span class='mybutton' " 
	treeString += " tabindex='0' role='button' aria-pressed='false' "
	treeString += " id='buttonDetails"+obj[node].id+"' "
	treeString += " onclick=\"toggleElement('Details"+obj[node].id+"', 'arrow')\" "
	treeString += " title='Show / Hide contact-details.'>"
	treeString += "&nbsp;&triangleleft;&nbsp;"
	treeString += "</span> ";

	// contact details (telephone, URL, notes, ...)
	treeString += "   <span class='class_for_details' style='display:none' id='Details"+obj[node].id+"'>"+obj[node].details+"</span>";
	// treeString += "  </details> ";
	treeString +=  "</div>";

	//	Create a new <ol>-element with ID "olp00" for the children of the parent <li>.
	if (sons.length > 0) 
	{
		treeString += "<ol id='ol"+obj[node].id+"'>";

		for (var i in sons) 
		{
		treeString += buildTree(obj, sons[i]);
		}
		treeString += "</ol>";
	}
	return treeString;
}


// Hide / Show the lower <ol><li>-elements.
// https://medium.com/@ryan_forrester_/hide-and-show-elements-in-javascript-a-complete-guide-e44871f15774
function toggleElement(elementId, style) {
	const element = document.getElementById(elementId);
	const originalDisplay = element.dataset.display || 'block';

	var toggle_button = "button"+element.id;

	if (element.style.display === 'none') {
		element.style.display = originalDisplay;

		if (style == "folder") 
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&#x1F5C0;&nbsp;";
		} 
		else if (style == "arrow")
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&triangledown;&nbsp;";
		}
		else
		{
		//	document.getElementById(toggle_button).innerHTML  = "0";
		}
	} 
	else 
	{
		element.dataset.display = element.style.display || getComputedStyle(element).display;
		element.style.display = 'none';		

		if (style == "folder") 
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&#x1F5C1;&nbsp;";
		} 
		else if (style == "arrow")
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&triangleleft;&nbsp;";
		}
		else
		{
		//	document.getElementById(toggle_button).innerHTML  = "0";
		}
	}
}


// Create a <select><option> box at the MAIN CONTACT to show/hide the different levels of contacts
// Example: level_1 = main contact, level_2: categories, level_3: people / parents, level_4: children
function build_select_form_for_levels() {

	var select_form = "";
	select_form += "<select title='Show / Hide all elements to the specific level.'>";

	// Test up to ten levels of contacts but skip level 1 (main person) and 2 (categories)
	for (var i = 2; i <= 99; i++) {

		// Add <ol><li>-levels for the querySelectorAll-search
		var li_ol = ">li>ol".repeat(i)
		var ol_li_child = document.querySelectorAll('#contact-chart'+li_ol);

		// If there's anything in the <ol><li>-part, we have a valid level
		if (ol_li_child.length > 0) {
			select_form += "<option "
			select_form += " id='option_level_"+i+"' "
			select_form += " onclick='toggle_levels("+i+")'>"
			select_form += "&nbsp;&#x1F5C0;&nbsp; "+(i+1)+" "
			select_form += "</option>"
		}
	}
	select_form += "</select>";

	// Add it to the main person's <div>
	document.getElementById("mainPerson").innerHTML += select_form

}

// Show / Hide the different contact-levels (<ol><li>) 
function toggle_levels(level) {

	var display_state_none = 0
	var display_state_block = 0
	var display_state_to_set = ""
	var icon_to_set = ""

	// Add <ol><li>-levels for the querySelectorAll-search
	// Example: level 3 = 3x ">li>ol" 
	var li_ol = ">li>ol".repeat(level)

	// Define the level to search for. 
	// Example: level 3 = "#contact-chart >li>ol >li>ol >li>ol"
	var list_items = document.querySelectorAll('#contact-chart'+li_ol);

	// Go through the <ol><li>-levels and find the current display-state of the given level
	for (var i = 0; i < list_items.length; i++) 
	{
		// current state of display: "none" or "block"
		var state_of_display = list_items[i].style.display || getComputedStyle(list_items[i]).display;

		// Someone could have clicked on "Hide / Show". So the display state would be different from all the others in the same level.
		// That's why we're counting the different states, to see who has the most display-states.
		if (state_of_display == "none")
		{ 
			display_state_none++ 
		}
		else if (state_of_display == "block")
		{ 
			display_state_block++ 
		}
	}

	// If most display-states are on "block", we'll change it to "none"
	if (display_state_block > display_state_none)
	{
		display_state_to_set = "none"
		icon_to_set = "&nbsp;&#x1F5C1;&nbsp;"
	}
	// If most display-states are on "none", we'll change it to "block".
	else
	{
		display_state_to_set = "block"
		icon_to_set = "&nbsp;&#x1F5C0;&nbsp;"
	}


	// If we show the elements again (block), show ALL levels again down to level 2
	if (display_state_to_set == "block")
	{
		var last_level_to_change = 2
	}
	// If we hide the elements of this level (none), hide only up to the given level but leave everything else untouched.
	else
		var last_level_to_change = level


	// Go through all levels starting from 99 downwards and change the display-setting.
	for (var i = 99; i >= last_level_to_change; i--) 
	{ 
		var li_ol = ">li>ol".repeat(i)
		var list_items = document.querySelectorAll('#contact-chart'+li_ol);

		try 
		{
			var toggle_button = "option_level_"+i
			document.getElementById(toggle_button).innerHTML  = icon_to_set+" "+(i+1)
		}
		catch {}

		for (var j = 0; j < list_items.length; j++) 
		{
			list_items[j].style.display = display_state_to_set
		}
	}
}
