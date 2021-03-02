// IE NodeList.forEach polyfill.
// See: https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach#polyfill
if (window.NodeList && !NodeList.prototype.forEach) {
    NodeList.prototype.forEach = Array.prototype.forEach;
}

define(["jquery", "pat-base", "pat-registry"], function ($, Base, Registry) {
    var pattern = Base.extend({
        name: "datagridfield",
        trigger: ".pat-datagridfield",
        parser: "mockup",

        defaults: {
            // Default values for attributes
        },

        aa_cells_selector:
            ".auto-append .datagridwidget-cell, .auto-append .datagridwidget-block-edit-cell",

        init: function () {
            // When DOM model is ready execute this actions to wire up page logic.

            this.el = this.$el[0];
            this.el_body = this.el.querySelector(".datagridwidget-body");

            // Check if this widget is in auto-append mode
            // and store for later usage
            var aa = this.el.querySelectorAll(".auto-append").length > 0;
            this.$el.data("auto-append", aa);

            // Hint CSS
            if (aa) {
                this.el_body.classList.add("datagridwidget-body-auto-append");
            } else {
                this.el_body.classList.add("datagridwidget-body-non-auto-append"); // prettier-ignore
            }

            this.updateOrderIndex(false);

            if (!aa) {
                this.ensureMinimumRows();
            }

            // Bind the handlers to the auto append rows
            var aa_cells = this.el.querySelectorAll(this.aa_cells_selector);
            aa_cells.forEach(function (aa_cell) {
                aa_cell.addEventListener(
                    "focusout",
                    this.autoInsertRowHandler.bind(this)
                );
            }, this);

            this.getRows().forEach(function (row) {
                this.initRow(row);
            }, this);

            this.el.dispatchEvent(
                new Event("afterdatagridfieldinit", {
                    bubbles: true,
                    cancelable: true,
                })
            );
        },

        initRow: function (row) {
            row.querySelectorAll(".dgf--row-add").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.addRowAfter(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-delete").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.removeFieldRow(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-moveup").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.moveRowUp(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-movedown").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.moveRowDown(row);
                    }.bind(this)
                );
            }, this);
        },

        getRows: function () {
            // Return primary nodes with class of datagridwidget-row, they can be any tag: tr, div, etc.
            return this.el_body.querySelectorAll(".datagridwidget-row");
        },

        getVisibleRows: function () {
            // Get all visible rows of DGF
            // Incl. normal rows + AA row

            var rows = this.getRows();
            var filteredRows = $(rows).filter(function () {
                var $tr = $(this);
                return !$tr.hasClass("datagridwidget-empty-row");
            });
            return filteredRows;
        },

        autoInsertRowHandler: function (e) {
            // Handle auto insert events by auto append.
            var currnode = e.currentTarget;
            this.autoInsertRow(currnode);
        },

        autoInsertRow: function (currnode, ensureMinimumRows) {
            /**
             * Add a new row when changing the last row
             *
             * @param {Boolean} ensureMinimumRows we insert a special minimum row so the widget is not empty
             */

            // fetch required data structure
            var thisRow = this.getParentRow(currnode); // The new row we are working on

            if (!thisRow.classList.contains("auto-append")) {
                // We only auto-append when in the last row.
                return;
            }

            var $thisRow = $(thisRow);
            var autoAppendMode = $(this.el_body).data("auto-append");

            if ($thisRow.hasClass("minimum-row")) {
                // The change event was not triggered on real AA row,
                // but on a minimum ensured row (row 0).
                // 1. Don't add new row
                // 2. Make widget to "normal" state now as the user has edited the empty row so we assume it's a real row
                this.supressEnsureMinimum();
                return;
            }

            // Remove the auto-append functionality from the all rows in this widget
            var aa_cells = this.el.querySelectorAll(this.aa_cells_selector);
            aa_cells.forEach(function (aa_cell) {
                aa_cell.removeEventListener(
                    "focusout",
                    this.autoInsertRowHandler
                );
            }, this);
            this.el.querySelectorAll(".auto-append").forEach(function (aa_row) {
                aa_row.classList.remove("auto-append");
            }, this);

            // Create a new row
            var newtr = this.createNewRow(thisRow),
                $newtr = $(newtr);
            // Add auto-append functionality to our new row
            $newtr.addClass("auto-append");

            /* Put new row to DOM tree after our current row.  Do this before
             * reindexing to ensure that any Javascript we insert that depends on
             * DOM element IDs (such as plone.formwidget.autocomplete) will
             * pick up this row before any IDs get changed.  At this point,
             * we techinically have duplicate TT IDs in our document
             * (one for this new row, one for the hidden row), but jQuery
             * selectors will pick up elements in this new row first.
             */

            this.$el.trigger("beforeaddrowauto", [this.$el, newtr]);

            if (ensureMinimumRows) {
                // Add a special class so we can later deal with it
                $newtr.addClass("minimum-row");
                $newtr.insertBefore(thisRow);
            } else {
                $newtr.insertAfter(thisRow);
            }

            // Re-enable auto-append change handler feature on the new auto-appended row
            var aa_cells = this.el.querySelectorAll(this.aa_cells_selector);
            aa_cells.forEach(function (aa_cell) {
                aa_cell.addEventListener(
                    "focusout",
                    this.autoInsertRowHandler.bind(this)
                );
            }, this);

            this.reindexRow(newtr, "AA");

            // Update order index to give rows correct values
            this.updateOrderIndex(true, ensureMinimumRows);
            this.$el.trigger("afteraddrowauto", [this.$el, newtr]);
        },

        addRowAfter: function (row) {
            /**
             * Creates a new row after the the target row.
             *
             * @param {Object} row DOM <tr>
             */

            // fetch required data structure
            var newtr = this.createNewRow();
            this.$el.trigger("beforeaddrow", [this.$el, newtr]);
            var filteredRows = this.getVisibleRows();

            // If using auto-append we add the "real" row before AA
            // We have a special case when there is only one visible in the gid
            if (
                row.classList.contains("auto-append") &&
                !row.classList.contains("minimum-row")
            ) {
                $(newtr).insertBefore(row);
            } else {
                $(newtr).insertAfter(row);
            }

            // Ensure minimum special behavior is no longer needed as we have now at least 2 rows
            if (row.classList.contains("minimum-row")) {
                this.supressEnsureMinimum();
            }

            // update orderindex hidden fields
            this.updateOrderIndex(true);
            this.$el.trigger("afteraddrow", [this.$el, newtr]);
        },

        createNewRow: function () {
            /**
             * Creates a new row.
             *
             * The row is not inserted to the table, but is returned.
             */

            // hidden template row
            var emptyRow = $(this.el_body)
                .children(".datagridwidget-empty-row")
                .first();
            if (emptyRow.size() === 0) {
                // Ghetto assert()
                throw new Error("Could not locate empty template row in DGF");
            }
            var $new_row = emptyRow
                .clone(true)
                .removeClass("datagridwidget-empty-row");

            this.initRow($new_row[0]);

            // enable patternslib
            $new_row
                .find('*[class^="dgw-disabled-pat-"]')
                .attr("class", function (i, cls) {
                    return cls.replace(/dgw\-disabled-pat-/, "pat-");
                });
            Registry.scan($new_row);
            return $new_row;
        },

        removeFieldRow: function (row) {
            /* Remove the row in which the given node is found */
            $(row).remove();

            // ensure minimum rows in non-auto-append mode, reindex if no
            // minimal row was added, otherwise reindexing is done by ensureMinimumRows
            if (
                $(this.el_body).data("auto-append") ||
                !this.ensureMinimumRows()
            ) {
                this.updateOrderIndex(false);
            }
        },

        moveRow: function (row, direction) {
            /* Move the given row down one */
            var nextRow;
            var rows = this.getRows();
            var idx = null;

            // We can't use nextSibling because of blank text nodes in some browsers
            // Need to find the index of the row
            $(rows).each(function (i) {
                if (this == row) {
                    idx = i;
                }
            });

            // Abort if the current row wasn't found
            if (idx == null) return;

            // The up and down should cycle through the rows, excluding the auto-append and
            // empty-row rows.
            var validrows = 0;
            $(rows).each(function (i) {
                if (
                    !$(this).hasClass("datagridwidget-empty-row") &&
                    !$(this).hasClass("auto-append")
                ) {
                    validrows += 1;
                }
            });

            if (idx + 1 == validrows) {
                if (direction == "down") {
                    this.moveRowToTop(row);
                } else {
                    nextRow = rows[idx - 1];
                    this.shiftRow(nextRow, row);
                }
            } else if (idx === 0) {
                if (direction == "up") {
                    this.moveRowToBottom(row);
                } else {
                    nextRow = rows[parseInt(idx + 1, 10)];
                    this.shiftRow(row, nextRow);
                }
            } else {
                if (direction == "up") {
                    nextRow = rows[idx - 1];
                    this.shiftRow(nextRow, row);
                } else {
                    nextRow = rows[parseInt(idx + 1, 10)];
                    this.shiftRow(row, nextRow);
                }
            }
            this.updateOrderIndex();
            this.$el.trigger("aftermoverow", [this.$el, row]);
        },

        moveRowDown: function (row) {
            this.moveRow(row, "down");
        },

        moveRowUp: function (row) {
            this.moveRow(row, "up");
        },

        shiftRow: function (bottom, top) {
            /* Put node top before node bottom */
            $(top).insertBefore(bottom);
        },

        moveRowToTop: function (row) {
            var rows = this.getRows();
            $(row).insertBefore(rows[0]);
        },

        moveRowToBottom: function (row) {
            var rows = this.getRows();

            // make sure we insert the directly above any auto appended rows
            var insert_after = 0;
            $(rows).each(function (i) {
                if (
                    !$(this).hasClass("datagridwidget-empty-row") &&
                    !$(this).hasClass("auto-append")
                ) {
                    insert_after = i;
                }
            });
            $(row).insertAfter(rows[insert_after]);
        },

        reindexRow: function (row, newindex) {
            /**
             * Fixup all attributes on all child elements that contain
             * the row index. The following attributes are scanned:
             * - name
             * - id
             * - for
             * - href
             * - data-fieldname
             *
             * On the server side, the DGF logic will rebuild rows based
             * on this information.
             *
             * If indexing for some reasons fails you'll get double
             * input values and Zope converts inputs to list, failing
             * in funny ways.
             *
             * @param  {DOM} row
             * @param  {Number} newindex
             */

            var $tbody = $(this.el_body);
            var name_prefix = $tbody.data("name_prefix") + ".";
            var id_prefix = $tbody.data("id_prefix") + "-";
            var $row = $(row);
            var oldindex = $row.data("index");

            function replaceIndex(el, attr, prefix) {
                if (el.attr(attr)) {
                    var val = el.attr(attr);
                    var pattern = new RegExp("^" + prefix + oldindex);
                    el.attr(attr, val.replace(pattern, prefix + newindex));
                    if (attr.indexOf("data-") === 0) {
                        var key = attr.substr(5);
                        var data = el.data(key);
                        el.data(key, data.replace(pattern, prefix + newindex));
                    }
                }
            }

            // update index data
            $row.data("index", newindex);
            $row.attr("data-index", newindex);

            $row.find('[id^="formfield-' + id_prefix + '"]').each(function (
                i,
                el
            ) {
                replaceIndex($(el), "id", "formfield-" + id_prefix);
            });
            $row.find('[name^="' + name_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "name", name_prefix);
            });
            $row.find('[id^="' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "id", id_prefix);
            });
            $row.find('[for^="' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "for", id_prefix);
            });
            $row.find('[href*="#' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "href", "#" + id_prefix);
            });
            $row.find('[data-fieldname^="' + name_prefix + '"]').each(function (
                i,
                el
            ) {
                replaceIndex($(el), "data-fieldname", name_prefix);
            });
        },

        supressEnsureMinimum: function () {
            /**
             * Stop ensure miminum special behavior.
             *
             * The caller is responsible to check there was one and only one minimum-row in the table.
             *
             * Call when data is edited for the first time or a row added.
             */

            // Remove the auto-append functionality from the all rows in this widget
            var aa_cells = this.el.querySelectorAll(this.aa_cells_selector);
            aa_cells.forEach(function (aa_cell) {
                aa_cell.removeEventListener(
                    "focusout",
                    this.autoInsertRowHandler
                );
            }, this);
            this.el.querySelectorAll(".auto-append").forEach(function (aa_row) {
                aa_row.classList.remove("auto-append");
            }, this);
            this.el.querySelectorAll(".minimum-row").forEach(function (aa_row) {
                aa_row.classList.remove("minimum-row");
            }, this);

            this.updateOrderIndex(true, false);
        },

        updateOrderIndex: function (backwards, ensureMinimumRows) {
            /**
             * Update all row indexes on a DGF table.
             *
             * Each <tr> and input widget has recalculated row index number in its name,
             * so that the server can then parsit the submitted data in the correct order.
             *
             * @param  {Boolean} backwards iterate rows backwards
             * @param  {Boolean} ensureMinimumRows We have inserted a special auto-append row
             */

            var $tbody = $(this.el_body);
            var name_prefix = $tbody.attr("data-name_prefix") + ".";
            var i, idx, row, $row, $nextRow;

            // Was this auto-append table
            var autoAppend = false;
            var rows = this.getRows();
            for (i = 0; i < rows.length; i++) {
                idx = backwards ? rows.length - i - 1 : i;
                (row = rows[idx]), ($row = $(row));

                if ($row.hasClass("datagridwidget-empty-row")) {
                    continue;
                }
                if ($row.hasClass("auto-append")) {
                    autoAppend = true;
                }
                this.reindexRow(row, idx);
            }

            // Handle a special case where
            // 1. Widget is empty
            // 2. We don't have AA mode turned on
            // 3. We need to have minimum editable row count of 1
            if (ensureMinimumRows) {
                this.reindexRow(rows[0], "AA");
                autoAppend = true;
            }

            // Add a special first and class row classes
            // to hide manipulation handles
            // AA handling is different once again
            var visibleRows = this.getVisibleRows();
            for (i = 0; i < visibleRows.length; i++) {
                (row = visibleRows[i]), ($row = $(row));
                if (i < visibleRows.length - 2) {
                    $nextRow = $(visibleRows[i + 1]);
                }
                if (i === 0) {
                    $row.addClass("datagridfield-first-filled-row");
                } else {
                    $row.removeClass("datagridfield-first-filled-row");
                }
                // Last visible before AA
                if (autoAppend) {
                    if ($nextRow && $nextRow.hasClass("auto-append")) {
                        $row.addClass("datagridfield-last-filled-row");
                    } else {
                        $row.removeClass("datagridfield-last-filled-row");
                    }
                } else {
                    if (i == visibleRows.length - 1) {
                        $row.addClass("datagridfield-last-filled-row");
                    } else {
                        $row.removeClass("datagridfield-last-filled-row");
                    }
                }
            }

            // Set total visible row counts and such and hint CSS
            var vis = this.getVisibleRows().length;
            $tbody.attr("data-count", this.getRows().length);
            $tbody.attr("data-visible-count", this.getVisibleRows().length);
            $tbody.attr("data-many-rows", vis >= 2 ? "true" : "false");

            $(document)
                .find('input[name="' + name_prefix + 'count"]')
                .each(function () {
                    // do not include the TT and the AA rows in the count
                    var count = rows.length;
                    if (
                        $(rows[count - 1]).hasClass("datagridwidget-empty-row")
                    ) {
                        count--;
                    }
                    if ($(rows[count - 1]).hasClass("auto-append")) {
                        count--;
                    }
                    this.value = count;
                });
        },

        getParentRow: function (node) {
            var parent = node.closest(".datagridwidget-row");
            if (parent) {
                return parent;
            }
            return null;
        },

        ensureMinimumRows: function () {
            /**
             * Make sure there is at least one visible row available in DGF
             * to edit in all the time.
             *
             * We need a lot of special logic for the case where
             * we have empty datagridfield and need to have one OPTIONAL
             * row present there for the editing when the user opens
             * the form for the first time.
             *
             * There are cases where one doesn't want to have the count of DGF
             * rows to go down to zero. Otherwise there no insert handle left
             * on the edit mode and the user cannot add any more rows.
             *
             * One should case is when
             *
             * - DGF is empty on new form
             *
             * - Auto append is set to false (initial row is not visible)
             *
             * We fix this situation by checking the available rows
             * and generating one empty AA row if needed.
             *
             * ... or simply when the user removes all the rows
             */

            var rows = this.getRows();
            var filteredRows = this.getVisibleRows();
            var self = this;

            // Rows = 0 -> make one AA row available
            if (filteredRows.length === 0) {
                // XXX: make the function call signatures more sane
                var child = rows[0];
                this.autoInsertRow(child, true);
                return true;
            }
            return false;
        },
    });

    return pattern;
});
