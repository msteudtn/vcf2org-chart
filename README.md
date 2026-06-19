# vcf2org-chart
Contacts to organization-chart converter

## Description

A python script, that converts your **address-book into an organigram**. 
The conversion is being processed privacy-friendly offline.

As a result, you can find out, how you know whom. This is based on the idea of "six degrees of separation". https://en.wikipedia.org/wiki/Six_degrees_of_separation

Example: Your buddy Frank (6) is married to Eve (5). She is a colleague of David (4), who plays football with Charlie (3). He is the neighbor of Bob (2), who is the brother to your wife Alice (1).

To run, type `vcf2chart.py FILENAME.VCF` or `vcf2chart.py "../another-folder/FILENAME.VCF"` depending on where the file is located.
It creates a file `index_contacts.html` and should start your browser.

![example of a contact organization chart](https://raw.githubusercontent.com/msteudtn/vcf2org-chart/refs/heads/main/assets/example.png)

## Prerequisites (you need ...)

* Your address-book exported as a **vCard VCF-file**. Please refer to your email / contact / messenger-application. You can find a short example of a VCF-file for the TV-show character Homer Simpson.

* Some hashtags in the NOTE of your contacts
  * **Three hashes** for your own contact details.  
    Example: `###this_is_me` or `###abcdef` or simply `###`
  * **Two hashes** for your "categories". These are the parent-elements.  
    Example `##work, ##friends, ##football`
  * **One hash** for the child-elements.
    Example: `#work, #friends, #football`
  * A child can also be parent to other children.
    Example: parent A: `##sports` -> has child B: with `#sports`. But B is also labeled parent for `##football` to -> child C: `#football`
  * A child overrules the category.
    Example: `My family + #sports` -> The contact will be under `##sports` but not `My family`.

* Optionally: Normal categories (sometimes called "label") on your contacts. Example: `My family, Friends`

* Python in version 3.x or higher

## Customization (optional)

### How to choose specific elements from the vCard?
Within the script, find the `list_of_vcf_property_types` in the first lines. You always need the **first four elements**!  
`list_of_vcf_property_types  = ["FN", "NOTE", " ", "CATEGORIES"]`  
But you can add more if you like.  
`list_of_vcf_property_types = ["FN", "NOTE", " ", "CATEGORIES", "ADR", "TEL", "EMAIL", "BDAY", "URL", "PHOTO"]`  
A list of properties can be found on Wikipedia https://en.wikipedia.org/wiki/VCard#Properties

### How to change the default depth of shown contacts at the beginning?
The HTML file shows only the first three levels by default. `(1: You, 2:Categories / first parents, 3:First children)`  
Within the `assets/treeData.js` find the function `toggle_levels(3)` and change it to another number.  
Example: `toggle_levels(5)`

### How to change the colors of the name-boxes?
Within the stylesheets in `àssets/css_org_chart.css` find the `:root`-part. It defines the **background-colors** for up to ten contact-levels.
The **text-color** (black / white) is calculated automatically based on the background using the CSS `contrast-color`.

## Known bugs

* **Multiple** #children or categories within one contact are **not possible**.  
Example: "Test Contact - with multiple categories" -> `CATEGORIES:Friends,My Family` -> last one is taken  
Example: "Test Contact - with multiple children" -> `NOTE:#burns #bart` -> last one is taken

* Extra labels **aren't filtered**.  
  * Example: Homer Simpsons (**with** extra labels)  
	  `TEL;TYPE=WORK:555-7334`  
	  `TEL;TYPE=HOME:555-6832`  
	   result: `TYPE=WORK:555-7334 TYPE=HOME:555-6832`
  * Example: Montgomery Burns (without extra labels)  
	  `TEL:(636) 555-0113`  
	  result: `(636) 555-0113`

* **Hashtags** should have **a space character in front** of them. If not, they can cause a mismatch with long texts before the hash tag in the NOTE-part.  
Example: `A very long note on a person and a hash tag that follows #child`  
could turn in the VCF file into  
`NOTE:A very long note on a person and a hash tag that follows `  
` #child`  
which then is processed into:  
`A very long note on a person and a hash tag that follows#child`

* There are different ways to specify a **photo**. The browser needs a string like `data:image/png;base64,[base64-data]` to show the data. So far, not all **possible scenarios** are covered currently.  
Examples: `PHOTO:TYPE=PNG;ENCODING=b:[base64-data]` or `PHOTO:ENCODING=BASE64;TYPE=PNG:[base64-data]` or `PHOTO;MEDIATYPE=image/png:http://example.com/logo.png`


## Development and license

There is probably space for many improvements. :) Feel free to open an issue, write to me at `mathias . steudtner (a) mailbox . org` or use it for your own projects. 

The scripts (python, HTML, CSS, JavaScript) are licensed under MIT license.  
https://choosealicense.com/licenses/mit/ 

Images and texts can be used under Creative Commons Attribution Share Alike 4.0 International (CC BY SA 4.0)  
https://choosealicense.com/licenses/cc-by-sa-4.0/

