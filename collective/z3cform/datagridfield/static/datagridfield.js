dataGridField2Functions = new Object();

(function($) {
  $(document).ready(function(){

    dataGridField2Functions.getInputOrSelect = function(node) {
        /* Get the (first) input or select form element under the given node */
        
        var inputs = node.getElementsByTagName("input");
        if(inputs.length > 0) {
            return inputs[0];
        }
        
        var selects = node.getElementsByTagName("select");
        if(selects.length > 0) {
            return selects[0];
        }

        return null;
    }

    dataGridField2Functions.getWidgetRows = function(currnode) {
        /* Return primary <tr>s of current node's parent DGW */
        tbody = this.getParentElementById(currnode, "datagridwidget-tbody");
        return this.getRows(tbody);
    }

    dataGridField2Functions.getRows = function(tbody) {
        /* Return <tr> rows of <table> element */
        
        var rows = new Array()
        
        child = tbody.firstChild;
        while(child != null) {
            if(child.tagName != null) {
                if(child.tagName.toLowerCase() == "tr") {
                    rows = rows.concat(child);
                }
            }
            child = child.nextSibling;
        }
                      
        return rows;   
    } 

    dataGridField2Functions.autoInsertRow = function(e) {
        /* Add a new row when changing the last row 
           (i.e. the infamous auto insert feature)
        
         */
        var currnode = window.event ? window.event.srcElement : e.currentTarget;


        // fetch required data structure   
        var tbody = dataGridField2Functions.getParentElement(currnode, "TBODY");
        var rows = dataGridField2Functions.getRows(tbody);        
        var lastRow = rows[rows.length-1]; 
        
        var thisRow = dataGridField2Functions.getParentElementById(currnode, "datagridwidget-row");      
        $(thisRow).removeClass('auto-append');
        dataGridField2Functions.reindexRow(tbody, thisRow, 0); /* updateOrderIndex will give it the right value later */
        $(thisRow).find('td.datagridwidget-cell').children().each(function(){
            $(this).unbind('change');
        });
        
        /* Skip the very last row which is a hidden template row */
        if (rows.length-1 == (thisRow.rowIndex)) {
            // Create a new row
            var newtr = dataGridField2Functions.createNewRow(lastRow);
            $(newtr).addClass('auto-append');
            $(newtr).find('td.datagridwidget-cell').children().each(function(){
                $(this).change(dataGridField2Functions.autoInsertRow);
            });
            dataGridField2Functions.reindexRow(tbody, newtr, 'AA');
                                                                
            // Put new row to DOM tree before template row        
            lastRow.parentNode.insertBefore(newtr, lastRow);
            
            // update orderindex hidden fields
            dataGridField2Functions.updateOrderIndex(tbody);	        	    
        }    
    }

    dataGridField2Functions.addRowAfter = function(currnode) {
        /*
            Creates a new row before the clicked row
        */
        
        // fetch required data structure
        var tbody = this.getParentElementById(currnode, "datagridwidget-tbody"); 
        var thisRow = this.getParentElementById(currnode, "datagridwidget-row"); 

        var newtr = this.createNewRow(thisRow);
            
        thisRow.parentNode.insertBefore(newtr, thisRow);
        
        // update orderindex hidden fields
        this.updateOrderIndex(tbody);	
      
    }

    dataGridField2Functions.addRow = function(id) {
        /* Explitcly add row for given dataGridField2 
        
            @param id Archetypes field id for the widget	
        */
        
        // fetch required data structure
        var tbody = document.getElementById("datagridwidget-tbody-" + id);    
        var rows = this.getRows(tbody);    
        var lastRow = rows[rows.length-1];
            
        var oldRows = rows.length;
                      
        // Create a new row
        var newtr = this.createNewRow(lastRow);
        
        // Put new row to DOM tree before template row        
        newNode = lastRow.parentNode.insertBefore(newtr, lastRow);
        $(newNode).removeClass('datagridwidget-empty-row');
        
        // update orderindex hidden fields
        this.updateOrderIndex(tbody);		
          
    }

    dataGridField2Functions.createNewRow = function(tr) { 
        /* Creates a new row 
               
           @param tr A row in a table where we'll be adding the new row
        */
        
        var tbody = this.getParentElementById(tr, "datagridwidget-tbody"); 
        var rows = this.getRows(tbody);   
        
        // hidden template row 
        var lastRow = rows[rows.length-1]; 
        
        var newtr = document.createElement("tr");
        newtr.setAttribute("id", "datagridwidget-row");
        newtr.setAttribute("class", "datagridwidget-row");
            
        // clone template contents from the last row to the newly created row
        // HOX HOX HOX
        // If f****ng IE clones lastRow directly it doesn't work.
        // lastRow is in hidden state and no matter what you do it remains hidden.
        // i.e. overriding class doesn't bring it visible.
        // In Firefox everything worked like a charm.
        // So the code below is really a hack to satisfy Microsoft codeborgs.
        // keywords: IE javascript clone clonenode hidden element render visibility visual
        child = lastRow.firstChild;
        while(child != null) {
            newchild = child.cloneNode(true);
            newtr.appendChild(newchild);
            child = child.nextSibling;
        }		
            
        return newtr;	 
    }


    dataGridField2Functions.removeFieldRow = function(node) {
        /* Remove the row in which the given node is found */
        
        var row = this.getParentElementById(node, 'datagridwidget-row');
        var tbody = this.getParentElementById(node, 'datagridwidget-tbody');
        tbody.removeChild(row);
        this.updateOrderIndex(tbody);	        	    
    }

    dataGridField2Functions.moveRowDown = function(currnode){
        /* Move the given row down one */
               
        var tbody = this.getParentElementById(currnode, "datagridwidget-tbody");    
        
        var rows = this.getWidgetRows(currnode);
        
        var row = this.getParentElementById(currnode, "datagridwidget-row");      
        if(row == null) {
            alert("Couldn't find DataGridWidget row");
            return;
        }
        
        var idx = null
        
        // We can't use nextSibling because of blank text nodes in some browsers
        // Need to find the index of the row
        for(var t = 0; t < rows.length; t++) {
            if(rows[t] == row) {
                idx = t;
                break;
            }
        }

        // Abort if the current row wasn't found
        if(idx == null)
            return;     
            
        // If this was the last row (before the blank row at the end used to create
        // new rows), move to the top, else move down one.
        if(idx + 2 == rows.length) {
            var nextRow = rows.item[0]
            this.shiftRow(row, nextRow)
        } else {
            var nextRow = rows[idx+1]
            this.shiftRow(nextRow, row)
        }
        
        this.updateOrderIndex(tbody)

    }

    dataGridField2Functions.moveRowUp = function(currnode){
        /* Move the given row up one */
        
        var tbody = this.getParentElementById(currnode, "datagridwidget-tbody");    
        var rows = this.getWidgetRows(currnode);
        
        var row = this.getParentElementById(currnode, "datagridwidget-row");      
        if(row == null) {
            alert("Couldn't find DataGridWidget row");
            return;
        }

        var idx = null
        
        // We can't use nextSibling because of blank text nodes in some browsers
        // Need to find the index of the row
        for(var t = 0; t < rows.length; t++) {
            if(rows[t] == row) {
                idx = t;
                break;
            }
        }
        
        // Abort if the current row wasn't found
        if(idx == null)
            return;
            
        // If this was the first row, move to the end (i.e. before the blank row
        // at the end used to create new rows), else move up one
        if(idx == 0) {
            var previousRow = rows[rows.length - 1]
            this.shiftRow(row, previousRow);
        } else {
            var previousRow = rows[idx-1];
            this.shiftRow(row, previousRow);
        }
        
        this.updateOrderIndex(tbody);
    }

    dataGridField2Functions.shiftRow = function(bottom, top){
        /* Put node top before node bottom */
        
        bottom.parentNode.insertBefore(bottom, top)   
    }

    dataGridField2Functions.reindexRow = function (tbody, row, newindex) {
        var data=$(tbody).data();
        var name_prefix = data.name_prefix + '.';
        var id_prefix = data.id_prefix + '-';

        $(row).find('[name^="' + name_prefix +'"]').each(function(){
            var oldname = this.name.substr(name_prefix.length);
            var oldindex1 = oldname.split('.', 1)[0];
            var oldindex2 = oldname.split('-', 1)[0];
            /* Name fields can have '-' for empty values */
            var oldindex = 0;
            if (oldindex1.length < oldindex2.length)
            {
                oldindex = oldindex1;
            } else {
                oldindex = oldindex2;
            }
            this.name = name_prefix + newindex + oldname.substr(oldindex.length);
        });
        $(row).find('[id^="' + id_prefix +'"]').each(function(){
            var oldid = this.id.substr(id_prefix.length);
            var oldindex = oldid.split('-', 1)[0];
            this.id = id_prefix + newindex + oldid.substr(oldindex.length);
        });
    }


    dataGridField2Functions.updateOrderIndex = function (tbody) {

        /* Split from the dataGridField2 approach here - and just re-do
         * the numbers produced by z3c.form
         */
        var data=$(tbody).data();
        var name_prefix = data.name_prefix + '.';

        var rows = this.getRows(tbody); 
        for (var i=0; i<rows.length; i++) {
            var row = rows[i];
            if ($(row).hasClass('datagridwidget-empty-row') || $(row).hasClass('auto-append')) {
                continue
            }
            dataGridField2Functions.reindexRow(tbody, row, i);
        }

        $(document).find('input[name="' + name_prefix + 'count"]').each(function(){
            // do not include the TT and the AA rows in the count
            var count = rows.length;
            if ($(rows[count-1]).hasClass('datagridwidget-empty-row')) {
                count--;
            }
            if ($(rows[count-1]).hasClass('auto-append')) {
                count--;
            }
            this.value = count;
        });
    }

    dataGridField2Functions.getParentElement = function(currnode, tagname) {
        /* Find the first parent node with the given tag name */

        tagname = tagname.toUpperCase();
        var parent = currnode.parentNode;

        while(parent.tagName.toUpperCase() != tagname) {
            parent = parent.parentNode;
            // Next line is a safety belt
            if(parent.tagName.toUpperCase() == "BODY") 
                return null;
        }

        return parent;
    }

    dataGridField2Functions.getParentElementById = function(currnode, id) {
        /* Find the first parent node with the given id 
        
            Id is partially matched: the beginning of
            an element id matches parameter id string.
        
            Currnode: Node where ascending in DOM tree beings
            Id: Id string to look for. 
                    
        */
        
        id = id.toLowerCase();
        var parent = currnode.parentNode;

        while(true) {
           
            var parentId = parent.getAttribute("id");
            if(parentId != null) {    	
                 if(parentId.toLowerCase().substring(0, id.length) == id) break;
            }
                
            parent = parent.parentNode;
            // Next line is a safety belt
            if(parent.tagName.toUpperCase() == "BODY") 
                return null;
        }

        return parent;
    }


    /* Bind the handlers to the auto append rows */
    $(document).find('table.datagridwidget-table-view').find('tr.auto-append').each(function() {
        $(this).find('td.datagridwidget-cell').children().each(function(){
            $(this).change(dataGridField2Functions.autoInsertRow);
        });
    });
  });
})(jQuery);

