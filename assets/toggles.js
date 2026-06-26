'use strict';

// Hide / Show the lower <ol><li>-elements.
// https://medium.com/@ryan_forrester_/hide-and-show-elements-in-javascript-a-complete-guide-e44871f15774
function toggleElement(elementId, icon_style) {

	// Remove any potential connection bezier-curve
	removeBezier();

	// Get the current DISPLAY-setting
	const element = document.getElementById(elementId);
	const originalDisplay = element.dataset.display || 'block';

	// Get the ID of the button, like "button_Details_p00" or "button_ol_p00"
	var toggle_button = "button_"+element.id;

	if (element.style.display === 'none') 
	{
		// Set the display state to BLOCK (visible)
		element.style.display = originalDisplay;

		// Set the icons 
		if (icon_style == "folder") 
		{
			var icon = ""
			icon += "&nbsp;&#x1F5C0;"; // Icon: closed folder
			icon += "<sub>"+document.getElementById(toggle_button).dataset.number;+"</sub>"

			document.getElementById(toggle_button).innerHTML  = icon;
		} 
		else if (icon_style == "arrow")
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&#x25BD;&nbsp;"; // Icon: arrow downwards
		}
		else
		{
			document.getElementById(toggle_button).innerHTML  = "?"; // This ELSE-case shouldn't happen
		}
	} 
	else 
	{
		// Set the display state to NONE (hidden)
		element.dataset.display = element.style.display || getComputedStyle(element).display;
		element.style.display = 'none';		

		// Set the icons 
		if (icon_style == "folder") 
		{
			var icon = ""
			icon += "&nbsp;&#x1F5C1;"; // Icon: open folder
			icon += "<sub>"+document.getElementById(toggle_button).dataset.number;+"</sub>"

			document.getElementById(toggle_button).innerHTML  = icon;
		} 
		else if (icon_style == "arrow")
		{
			document.getElementById(toggle_button).innerHTML  = "&nbsp;&#x25C1;&nbsp;"; // Icon: arrow left
		}
		else
		{
			document.getElementById(toggle_button).innerHTML  = "?"; // This ELSE-case shouldn't happen
		}
	}
}


// Create a <select><option> box at the MAIN CONTACT to show/hide the different levels of contacts
// Calls the function "toggle_levels()" from within.
// Example: level_1 = main contact, level_2: categories, level_3: people / parents, level_4: children
function build_select_form_for_levels() {

	var select_form = "";
	select_form += "<select title='Show / Hide all elements to the specific level.' ";
	select_form += " onchange=\"if (typeof(this.selectedIndex) != 'undefined') toggle_levels(this.value)\" "
	select_form += ">"

	// Test up to 99 levels of contacts but skip level 1 (main person, i = 0) and 2 (categories, i = 1). 
	for (var i = 2; i <= 99; i++) {

		// Add <ol><li>-levels for the querySelectorAll-search
		var li_ol = ">li>ol".repeat(i)
		var ol_li_child = document.querySelectorAll('#contact-chart'+li_ol);

		// If there's anything in the <ol><li>-part, we have a valid level and can create a <option>-tag
		if (ol_li_child.length > 0) {
			select_form += "<option "
			select_form += " id='option_level_"+i+"' "
			select_form += " value='"+(i+1)+"' >"
//			select_form += " onclick='toggle_levels("+i+")'>" // onlick() in <option> doesn't work on Chrome, but in Firefox.
			select_form += "&nbsp;&#x1F5C0;&nbsp; "+(i+1)+" "
			select_form += "</option>"
		}
	}
	select_form += "</select>";

	// Add the <select>-form to the main person's <div> -> <table> -> 1st row [0]
	// Example:
	//       |      | button DETAILS     | button CHILDREN | new cell with <select>
	// PHOTO | NAME | ------------------ | --------------- | ----------------------
	//       |      | button CONNECTIONS | empty           |

	var last_cell = document.querySelectorAll("#mainPerson > table")[0].rows[0] ; 
	last_cell.innerHTML += "<td>"+select_form+"</td>"
}


// Show / Hide ALL contact-levels to a specific level (<ol><li>) from the MAIN PERSON
// Is being called from the <select>-form from "build_select_form_for_levels()"
function toggle_levels(level) {

	// Remove any potential connection bezier-curve
	removeBezier();


	var display_state_none = 0
	var display_state_block = 0
	var display_state_to_set = ""
	var icon_to_set = ""

	// 1st run: Go through all levels starting from 99 downwards up to 2 ("categories") and change the display-setting to BLOCK. = Show all.
	for (var i = 99; i >= 2; i--) 
	{ 
		// Define the level to search for. 
		// Example: level 3 = "#contact-chart >li>ol >li>ol >li>ol"
		var li_ol = ">li>ol".repeat(i)
		var list_items = document.querySelectorAll('#contact-chart'+li_ol);

		// Set the icon for this level to "closed"
		try 
		{
			var toggle_button = "option_level_"+i
			document.getElementById(toggle_button).innerHTML  = "&#x1F5C0; "+(i+1) // Icon: closed folder
		}
		catch {}

		// Set the DISPLAY state to BLOCK (visible)
		for (var j = 0; j < list_items.length; j++) 
		{
			list_items[j].style.display = "block"
		}
	} // end of: for levels 99 -> 2 -> "BLOCK"


	// 2nd run: Go through all levels starting from 99 downwards up to LEVEL and change the display-setting to NONE. = Hide only up to selected level.
	for (var i = 99; i >= level; i--) 
	{ 

		// Define the level to search for. 
		// Example: level 3 = "#contact-chart >li>ol >li>ol >li>ol"
		var li_ol = ">li>ol".repeat(i)
		var list_items = document.querySelectorAll('#contact-chart'+li_ol);

		// Set the icon for this level to "open"
		try 
		{
			var toggle_button = "option_level_"+i
			document.getElementById(toggle_button).innerHTML  = "&#x1F5C1; "+(i+1) // Icon: open folder
		}
		catch {}

		// Set the DISPLAY state to NONE (hidden)
		for (var j = 0; j < list_items.length; j++) 
		{
			list_items[j].style.display = "none"
		}
	} // end of: for levels 99 -> level -> "NONE"
}


// Open all parent-items of a SPECIFIC ID.
// Used to draw the connection-Bezier path
// Example: "Ralph" (level 4) -> open "Lisa" (level 3) -> open "My Family" (level 2)
//          but do NOT open "Bart", "Maggie", "Marge"
function open_all_parents_of_id(childID)
{
	for (var i = 0; i <= 99; i++)
	{
		try 
		{
			// Get the new parent of this child-ID from the JSON-data.
			// Then, the parent becomes a new child-ID.
			// Look for this parent again.
			childID = tree[childID].parent
			// Change display to "block" to show it.
			document.getElementById("ol_"+childID).style.display = "block"
		}
		catch (error)
		{}
	}
}
