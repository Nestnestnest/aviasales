var fligtMenu = new Vue({
    el: '#main_flight_menu',
    data: {
        trip_data : [],
        currency : '',
        },

    created() {
    },
    mounted() {
    },
    methods: {
        getTrip(){
            console.log(this.$refs);
            from = this.$refs.form.FROM.value;
            to = this.$refs.form.TO.value;
            when = this.$refs.form.WHEN.value;
            when_return = this.$refs.form.WHEN_RETURN.value;
            who = this.$refs.form.WHO.value;
            xml = this.$refs.form.xml.value;

            if(this.currency == '' || this.currency == 1)
            local_zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            else
                local_zone = null;
            var data = new FormData();
            data.append('local_zone',local_zone);
            data.append('FROM',from);
            data.append('TO',to);
            data.append('WHEN',when);
            data.append('WHEN_return',when_return);
            data.append('WHO',who);
            data.append('xml',xml);
            $.ajax({
                type: 'POST',
                url: '/get_flight',
                contentType: false,
                data:data,
                processData: false,
                dataType: 'json'
            }).done(function (data) {
                console.log("TCL: getDataRender -> data", data)
            }.bind(this))
                .fail(function (data) {
                    console.log('fail');
                })
         },
        getDataRender() {
            $.ajax({
                type: 'POST',
                url: `/get_roles/${this.username}`,
                contentType: false,
                processData: false,
                dataType: 'json'
            }).done(function (data) {
                console.log("TCL: getDataRender -> data", data)
                this.parseData(data)
                loader(false)
            }.bind(this))
                .fail(function (data) {
                    console.log('fail');
                })
        },
        parseData(data) {
            this.addSearchString(data)
            data.users_roles = []
            if (data.edit_roles) {
                this.setViewStatus(data.edit_roles, 1)
                this.editableRoles = data.edit_roles
                data.users_roles = data.users_roles.concat(this.editableRoles)
            }
            else {
                this.editableRoles = []
            }

            if (data.read_roles) {
                this.setViewStatus(data.read_roles, 0)
                this.readableRoles = data.read_roles
                data.users_roles = data.users_roles.concat(this.readableRoles)
            }
            else {
                this.readableRoles = []
            }
            this.setViewStatus(data.all_roles, -1)
            this.allRoles = data.all_roles
            this.originData = JSON.parse(JSON.stringify(data))
            this.sortArraysByCodeRole([this.readableRoles, this.editableRoles, this.allRoles])
            this.bindInitialColSelect([{ arr: this.readableRoles, value: 'read' }, { arr: this.editableRoles, value: 'edit' }, { arr: this.allRoles, value: 'all' }])
            this.parseSelectsData(data)
        },
        addSearchString(data) {
            for (arr in data) {
                data[arr].forEach(role => {
                    role.string_data = ''
                    for (prop in role) {
                        role.string_data += `${role[prop]}-`
                    }
                })
            }
            console.log('STRING DATA', data)
        },
        bindInitialColSelect(arrs) {
            arrs.some(el => {
                if (el.arr != 0) {
                    this.selectedCol = el.value
                    return true
                }
                return false
            })
        },
        setViewStatus(arr, status) {
            arr.forEach(el => {
                el.viewStatus = status
            })
        },
        parseSelectsData() {
            this.pullOutSelectProps(this.allRoles, 'all')
            this.pullOutSelectProps(this.readableRoles, 'read')
            this.pullOutSelectProps(this.editableRoles, 'edit')
        },
        pullOutSelectProps(rolesArr, col) {
            for (key in this.selectedRoleOptions[col]) {
                this.selectedRoleOptions[col][key].splice(0, this.selectedRoleOptions[col][key].length)
            }
            rolesArr.forEach(role => {
                for (key in role) {
                    if (this.selectedRoleOptions[col][key]) {
                        this.selectedRoleOptions[col][key].push(role[key])
                    }
                    else {
                        this.$set(this.selectedRoleOptions[col], key, [])
                        this.selectedRoleOptions[col][key].push(role[key])
                    }
                }
            })
            for (arr in this.selectedRoleOptions[col]) {
                this.selectedRoleOptions[col][arr] = this.unique(this.selectedRoleOptions[col][arr])
            }
        },
        addRole(id, arrayToAdd) {
            if (arrayToAdd.indexOf(id) != -1) {
                const rolePosition = arrayToAdd.indexOf(id)
                arrayToAdd.splice(rolePosition, 1)
            }
            else {
                arrayToAdd.push(id)
            }
        },
        submitRoles(arrayFrom, arrayTo, arrayToLookForIndex, direction, actionType) {

            direction = direction.split('-')
            moveFrom = direction[0]
            moveTo = direction[1]
            arrayToLookForIndex.forEach(role => {
                const roleToAdd = arrayFrom.find(el => el.Code_Role == role)
                if (moveTo == "edit") {
                    roleToAdd.viewStatus = 1
                }
                else if (moveTo == "read") {
                    roleToAdd.viewStatus = 0
                }
                else {
                    roleToAdd.viewStatus = -1
                }
                const allRolesDeleteIndex = arrayFrom.findIndex(el => el.Code_Role == role)
                if (roleToAdd != undefined) {
                    arrayFrom.splice(allRolesDeleteIndex, 1)
                    arrayTo.unshift(roleToAdd)
                }
                this.addToChanges(roleToAdd, actionType)
            });
            this.pullOutSelectProps(arrayTo, moveTo)
            this.pullOutSelectProps(arrayFrom, moveFrom)
            this.bindInitialColSelect([{ arr: this.readableRoles, value: 'read' }, { arr: this.editableRoles, value: 'edit' }, { arr: this.allRoles, value: 'all' }])
            arrayToLookForIndex.splice(0, arrayToLookForIndex.length)
            this.activeToggleController = false
        },
        addToChanges(role, actionType) {
            if (actionType == 'add') {
                if (this.originData.users_roles.findIndex(el => el.Code_Role == role.Code_Role) != -1) {
                    if (this.changes.remove.findIndex(el => el.Code_Role == role.Code_Role) != -1) {
                        let cancelChangeIndex = this.changes.remove.findIndex(el => el.Code_Role == role.Code_Role)
                        this.changes.remove.splice(cancelChangeIndex, 1)
                    }
                    let compareElem = this.originData.users_roles.find(el => el.Code_Role == role.Code_Role)
                    if (compareElem.viewStatus == role.viewStatus) {
                        let cancelChangeIndex = this.changes.add.findIndex(el => el.Code_Role == role.Code_Role)
                        this.changes.add.splice(cancelChangeIndex, 1)
                    }
                    else {
                        this.changes.add.push(role)
                    }
                }
                else {
                    if (this.changes.add.findIndex(el => el.Code_Role == role.Code_Role) != -1) {
                        let cancelChangeIndex = this.changes.add.findIndex(el => el.Code_Role == role.Code_Role)
                        this.changes.add.splice(cancelChangeIndex, 1)
                        this.changes.add.push(role)
                    } else {
                        this.changes.add.push(role)
                    }
                }

            }
            else if (actionType == 'remove') {
                if (this.changes.add.findIndex(el => el.Code_Role == role.Code_Role) != -1) {
                    let cancelChangeIndex = this.changes.add.findIndex(el => el.Code_Role == role.Code_Role)
                    this.changes.add.splice(cancelChangeIndex, 1)
                }
                if (this.originData.all_roles.findIndex(el => el.Code_Role == role.Code_Role) != -1) {
                    let cancelChangeIndex = this.changes.add.findIndex(el => el.Code_Role == role.Code_Role)
                    this.changes.remove.splice(cancelChangeIndex, 1)
                }
                else {
                    this.changes.remove.push(role)
                }
            }
        },
        indexOfElement(el, arr) {
            return arr.indexOf(el) != -1 ? true : false
        },
        findElemInArray(arr, el, prop) {
            return arr.find(arrEl => arrEl[prop] == el[prop])
        },
        submitChanges() {
            loader(true)
            var submit_data = new FormData();
            submit_data.append('changes', JSON.stringify(this.changes));
            $.ajax({
                type: 'POST',
                url: `/set_roles`,
                data: submit_data,
                contentType: false,
                processData: false,
                dataType: 'json'
            }).done(function (data) {
                this.cleanChangesArr()
                // this.getDataRender()
                loader(false)
            }.bind(this)).fail(function (data) {
                console.log('FAIL')
                loader(false)
            }.bind(this))
        },
        cleanChangesArr() {
            for (arr in this.changes) {
                if (arr != 'code_user') {
                    this.changes[arr] = []
                }
            }

            for (arr in this.selectedRoles) {
                this.selectedRoles[arr] = []
            }
        },
        cancelChanges() {
            this.parseData(this.originData)
            for (arr in this.selectedRoles) {
                this.selectedRoles[arr].splice(0, this.selectedRoles[arr].length)
            }
            for (arr in this.changes) {
                this.changes[arr] = []
            }
        },
        returnRolesAfterCancel(arrayTo, arrayFrom, codeRole) {
            const roleToReturn = arrayFrom.find(el => el.Code_Role == codeRole)
            const roleToReturnIndex = arrayFrom.findIndex(el => el.Code_Role == codeRole)
            arrayFrom.splice(roleToReturnIndex, 1)
            arrayTo.unshift(roleToReturn)
        },
        sortArraysByCodeRole(columnsArr) {
            columnsArr.forEach(el => {
                el.sort((a, b) => {
                    if (a.Code_Role > b.Code_Role) {
                        return 1;
                    }
                    if (a.Code_Role < b.Code_Role) {
                        return -1;
                    }
                    return 0;
                })
            })
        },
        pickOutRoles() {
            const colsArr = [{ arr: this.readableRoles, value: 'read' }, { arr: this.editableRoles, value: 'edit' }, { arr: this.allRoles, value: 'all' }]
            const arrWhereSelect = colsArr.find(el => el.value == this.selectedCol)
            arrWhereSelect.arr.forEach(el => {
                this.checkedRoles.forEach(prop => {
                    if (el[this.selectedLevel] == prop) {
                        this.addRole(el.Code_Role, this.selectedRoles[this.selectedCol])
                    }
                })
            })
            this.checkedRoles = []
        },
        resetPickedRoles() {
            for (arr in this.selectedRoles) {
                this.selectedRoles[arr] = []
            }
        },
        goToPrevPage() {
            window.location.href = window.location.origin + '/add_user'
        },
        toggleActiveRoles() {
            if (this.activeToggleController) {
                document.querySelectorAll(`.add-role__item-${this.selectedCol}`).forEach(el => {
                    if (!el.classList.contains('active')) {
                        el.style.display = 'none'
                    }
                })
            }
            else {
                document.querySelectorAll(`.add-role__item-${this.selectedCol}`).forEach(el => {
                    el.style.display = 'block'
                })
            }
        }
    },

    delimiters: ['[[', ']]']
})