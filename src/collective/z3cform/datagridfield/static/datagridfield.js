// IE NodeList.forEach polyfill.
// See: https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach#polyfill
if (window.NodeList && !NodeList.prototype.forEach) {
    NodeList.prototype.forEach = Array.prototype.forEach;
}

define(["jquery", "pat-base", "pat-registry"], function ($, Base, Registry) {
    var pattern = Base.extend({
        name: "datagridfield",
        trigger: ".pat-datagridfield",

        init: function () {
            // - Make sure, at least one empty row is always shown.
            // - Auto append a new row when editing the last row.

            this.el = this.$el[0];
            this.el_body = this.el.querySelector(".datagridwidget-body");

            this.auto_append = (this.el.dataset.autoAppend || "true").toLowerCase() !== "false"; // prettier-ignore

            this._defineHandler();

            // Before ensureMinimumRows, as creating a row initializes row ui again.
            this.getVisibleRows().forEach(function (row) {
                this.initRowUI(row);
            }, this);

            if (!this.ensureMinimumRows()) {
                // If ensureMinimumRows returned true, it already did the update.
                this.updateOrderIndex();
            }
            this.initAutoAppendHandler();

            this.el.dispatchEvent(
                new Event("afterdatagridfieldinit", {
                    bubbles: true,
                    cancelable: true,
                })
            );
        },

        _defineHandler: function () {
            // Store event handler which also has to be removed, so we can detach it.
            // See: https://stackoverflow.com/a/10444156/1337474 , also comment about "bind"
            // using ``bind`` will change the function signature too.

            this.handler_auto_append = function (e) {
                if (e) {
                    e.stopPropagation();
                }
                // Also allow direct call without event.
                if (e && !e.target.closest(".datagridwidget-cell")) {
                    return;
                }
                this.auto_append_row();
            }.bind(this);

            this.handler_auto_append_input = function (e) {
                var row = e.currentTarget;
                row.classList.remove("auto-append");
                row.dataset.oldIndex = row.dataset.index; // store for replacing.
                delete row.dataset.index; // remove "AA" index
                this.updateOrderIndex();
                row.removeEventListener(
                    "input",
                    this.handler_auto_append_input
                );
            }.bind(this);
        },

        initRowUI: function (row) {
            row.querySelectorAll(".dgf--row-add").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.insertRow(row);
                        this.updateOrderIndex();
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

        get_row_buttons: function (row) {
            return {
                add: row.querySelector(".dgf--row-add"),
                delete: row.querySelector(".dgf--row-delete"),
                up: row.querySelector(".dgf--row-moveup"),
                down: row.querySelector(".dgf--row-movedown"),
            };
        },

        setUIState: function () {
            var rows = this.getVisibleRows();
            for (var cnt = 0; cnt < rows.length; cnt++) {
                var row = rows[cnt];
                var buttons = this.get_row_buttons(row);

                if (row.dataset.index === "AA") {
                    // Special case AA

                    if (buttons.add) {
                        buttons.add.disabled = true;
                    }
                    if (buttons.delete) {
                        buttons.delete.disabled = true;
                    }
                    if (buttons.up) {
                        buttons.up.disabled = true;
                    }
                    if (buttons.down) {
                        buttons.down.disabled = true;
                    }
                    if (cnt > 0) {
                        // Set the previous buttons also, if available.
                        var before_aa_buttons = this.get_row_buttons(
                            rows[cnt - 1]
                        );
                        if (before_aa_buttons.down) {
                            before_aa_buttons.down.disabled = true;
                        }
                    }
                } else if (cnt === 0) {
                    // First row

                    if (buttons.add) {
                        buttons.add.disabled = false;
                    }
                    if (buttons.delete) {
                        buttons.delete.disabled = false;
                    }
                    if (buttons.up) {
                        buttons.up.disabled = true;
                    }
                    if (buttons.down) {
                        buttons.down.disabled = rows.length === 1; // disable if 1 row.
                    }
                } else if (cnt === rows.length - 1) {
                    // Last button - if no AA buttons.
                    // Also, if this is reached, it's not the only row.

                    if (buttons.add) {
                        buttons.add.disabled = false;
                    }
                    if (buttons.delete) {
                        buttons.delete.disabled = false;
                    }
                    if (buttons.up) {
                        buttons.up.disabled = false;
                    }
                    if (buttons.down) {
                        buttons.down.disabled = true;
                    }
                } else {
                    // Normal in-between case.

                    if (buttons.add) {
                        buttons.add.disabled = false;
                    }
                    if (buttons.delete) {
                        buttons.delete.disabled = false;
                    }
                    if (buttons.up) {
                        buttons.up.disabled = false;
                    }
                    if (buttons.down) {
                        buttons.down.disabled = false;
                    }
                }
            }
        },

        getRows: function () {
            // Return primary nodes with class of datagridwidget-row, they can be any tag: tr, div, etc.
            return this.el_body.querySelectorAll(".datagridwidget-row");
        },

        getVisibleRows: function () {
            return this.el_body.querySelectorAll(
                ".datagridwidget-row:not([data-index=TT])"
            );
        },

        getLastRow: function () {
            return this.el_body.querySelector(".datagridwidget-row:last-child");
        },

        getLastVisibleRow: function () {
            var result = this.el_body.querySelectorAll(
                ".datagridwidget-row:not([data-index=TT])"
            );
            return result[result.length - 1];
        },

        countRows: function () {
            var count = 0;
            this.getRows().forEach(function (row) {
                // do not include the TT and the AA rows in the count
                if (["AA", "TT"].indexOf(row.dataset.index) === -1) {
                    count++;
                }
            }, this);
            return count;
        },

        initAutoAppendHandler: function () {
            if (!this.auto_append) {
                return;
            }

            this.getVisibleRows().forEach(function (row) {
                row.removeEventListener("focusout", this.handler_auto_append);
            }, this);

            var last_row = this.getLastVisibleRow();
            if (last_row) {
                last_row.addEventListener("focusout", this.handler_auto_append);
            }
        },

        auto_append_row: function () {
            this.el.dispatchEvent(new Event("beforeaddrowauto"));
            this.getVisibleRows().forEach(function (row) {
                row.classList.remove("auto-append");
                if (row.dataset.index !== "TT") {
                    // actually, getVisibleRows should only return non-"TT"
                    // rows, but to be clear here...
                    // delete the index, we're setting it in updateOrderIndex again.
                    row.dataset.oldIndex = row.dataset.index; // store for replacing.
                    delete row.dataset.index;
                }
            });
            var last_row = this.getLastVisibleRow() || this.getLastRow();
            var new_row = this.insertRow(last_row);
            new_row.classList.add("auto-append");
            this.reindexRow(new_row, "AA");
            this.updateOrderIndex();
            new_row.addEventListener("input", this.handler_auto_append_input);
            this.el.dispatchEvent(new Event("afteraddrowauto"));
        },

        insertRow: function (ref_row, before) {
            /**
             * Add a new row when changing the last row
             *
             * @param {DOM node} ref_row insert row after this one.
             */

            // Create a new row
            var newtr = this.createNewRow();
            var $newtr = $(newtr);

            /* Put new row to DOM tree after our current row.  Do this before
             * reindexing to ensure that any Javascript we insert that depends on
             * DOM element IDs (such as plone.formwidget.autocomplete) will
             * pick up this row before any IDs get changed.  At this point,
             * we techinically have duplicate TT IDs in our document
             * (one for this new row, one for the hidden row), but jQuery
             * selectors will pick up elements in this new row first.
             */

            this.$el.trigger("beforeaddrow", [this.$el, $newtr]);

            if (before) {
                $newtr.insertBefore(ref_row);
            } else {
                $newtr.insertAfter(ref_row);
            }

            this.initAutoAppendHandler();

            this.$el.trigger("afteraddrow", [this.$el, $newtr]);

            return newtr;
        },

        createNewRow: function () {
            /**
             * Creates a new row.
             *
             * The row is not inserted to the table, but is returned.
             */

            // hidden template row
            var template_row = this.el_body.querySelector("[data-index=TT]");
            if (!template_row) {
                throw new Error("Could not locate empty template row in DGF");
            }

            var new_row = template_row.cloneNode(true);

            new_row.dataset.oldIndex = new_row.dataset.index; // store for replacing.
            delete new_row.dataset.index; // fresh row.
            new_row.classList.remove("datagridwidget-empty-row");

            this.initRowUI(new_row);

            var $new_row = $(new_row);
            // enable patternslib
            $new_row
                .find('*[class^="dgw-disabled-pat-"]')
                .attr("class", function (i, cls) {
                    return cls.replace(/dgw\-disabled-pat-/, "pat-");
                });
            Registry.scan($new_row);
            return new_row;
        },

        removeFieldRow: function (row) {
            /* Remove the row in which the given node is found */
            $(row).remove();

            if (!this.ensureMinimumRows()) {
                // If ensureMinimumRows returned true, it already did the update.
                this.updateOrderIndex();
            }
            this.updateOrderIndex();
            this.initAutoAppendHandler();
        },

        moveRowDown: function (row) {
            this.moveRow(row, "down");
            this.updateOrderIndex();
            this.initAutoAppendHandler();
        },

        moveRowUp: function (row) {
            this.moveRow(row, "up");
            this.updateOrderIndex();
            this.initAutoAppendHandler();
        },

        moveRowToTop: function (row) {
            var rows = this.getRows();
            $(row).insertBefore(rows[0]);
            this.updateOrderIndex();
            this.initAutoAppendHandler();
        },

        moveRowToBottom: function (row) {
            var rows = this.getRows();

            // make sure we insert the directly above any auto appended rows
            var insert_after = 0;
            $(rows).each(function (i, _row) {
                if (["AA", "TT"].indexOf(_row.dataset.index) === -1) {
                    insert_after = i;
                }
            });
            $(row).insertAfter(rows[insert_after]);
            this.updateOrderIndex();
            this.initAutoAppendHandler();
        },

        moveRow: function (row, direction) {
            /* Move the given row down one */
            var nextRow;
            var rows = this.getRows();
            var idx = null;

            // We can't use nextSibling because of blank text nodes in some browsers
            // Need to find the index of the row
            $(rows).each(function (i, _row) {
                if (row === _row) {
                    idx = i;
                }
            });

            // Abort if the current row wasn't found
            if (idx === null) {
                return;
            }

            // The up and down should cycle through the rows, excluding the auto-append and
            // empty-row rows.
            var validrows = this.countRows();

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
            this.$el.trigger("aftermoverow", [this.$el, row]);
        },

        shiftRow: function (bottom, top) {
            /* Put node top before node bottom */
            $(top).insertBefore(bottom);
        },

        reindexRow: function (row, new_index) {
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
             * @param  {Number} new_index
             */

            var name_prefix = this.el_body.dataset.name_prefix + ".";
            var id_prefix = this.el_body.dataset.id_prefix + "-";
            var old_index = row.dataset.oldIndex || row.dataset.index;
            delete row.dataset.oldIndex;

            function replaceIndex(el, attr, prefix) {
                var val = el.getAttribute(attr);
                if (val) {
                    var pattern = new RegExp("^" + prefix + old_index);
                    el.setAttribute(
                        attr,
                        val.replace(pattern, prefix + new_index)
                    );
                }
            }

            row.dataset.index = new_index; // update index data

            row.querySelectorAll('[id^="formfield-' + id_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "id", "formfield-" + id_prefix);
            }, this); // prettier-ignore
            row.querySelectorAll('[name^="' + name_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "name", name_prefix);
            }, this); // prettier-ignore
            row.querySelectorAll('[id^="' + id_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "id", id_prefix);
            }, this); // prettier-ignore
            row.querySelectorAll('[for^="' + id_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "for", id_prefix);
            }, this); // prettier-ignore
            row.querySelectorAll('[href*="#' + id_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "href", "#" + id_prefix);
            }, this); // prettier-ignore
            row.querySelectorAll('[data-fieldname^="' + name_prefix + '"]').forEach(function (el) {
                replaceIndex(el, "data-fieldname", name_prefix);
            }, this); // prettier-ignore
        },

        updateOrderIndex: function () {
            /**
             * Update all row indexes on a DGF table.
             *
             * Each <tr> and input widget has recalculated row index number in its name,
             * so that the server can then parsit the submitted data in the correct order.
             */

            var cnt = 0;
            var rows = this.getRows();
            rows.forEach(function (row) {
                var index = row.dataset.index;
                if (["AA", "TT"].indexOf(index) > -1) {
                    this.reindexRow(row, index);
                    return;
                }
                this.reindexRow(row, cnt);
                row.dataset.index = cnt;
                cnt++; // we start counting with "0"
            }, this);

            var name_prefix = this.el_body.dataset.name_prefix + ".";
            var count_el = this.el.querySelector(
                'input[name="' + name_prefix + 'count"]'
            );
            count_el.value = this.countRows();

            this.setUIState();
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

            // Rows = 0 -> make one AA row available
            if (rows.length && filteredRows.length === 0) {
                this.auto_append_row();
                return true;
            }
            return false;
        },
    });

    return pattern;
});
