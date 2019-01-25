import { Injectable } from "@angular/core";
import { PickerController, PickerColumn } from "ionic-angular";

export class SelectOption {
    name: string;
    value: any;
}

export class SelectOptionColumn {
    name: string;
    selectedValue: any;
    options: Array<SelectOption>;
    width?: string;
}

@Injectable()
export class SelectDialogController {
    
    constructor(
        private pickerCtrl: PickerController
    ) {}

    public choose(options:Array<SelectOption>, selectedValue?:any): Promise<any> {
        return this.showPicker([{
            name: 'selection',
            selectedValue: selectedValue,
            options: options
        }])
        .then((data) => {
            return data['selection'].value;
        })
    }

    public chooseMultiple(columns: Array<SelectOptionColumn>): Promise<any> {
        return this.showPicker(columns);
    }

    private showPicker(_columns:Array<SelectOptionColumn>) {
        return new Promise((resolve, reject) => {
            const buttons = [{
                text: 'Cancel',
                role: 'cancel',
                handler: reject
            }, {
                text: 'Select',
                handler: resolve
            }];

            const columns = _columns.map((column) => {
                let selectedIndex:number = null;
                const col: PickerColumn = {
                    name: column.name,
                    options: column.options.map((option, index) => {
                        if(option.value === column.selectedValue) {
                            selectedIndex = index;
                        }
                        return {
                            text: option.name,
                            value: option.value
                        }
                    })
                }
                if(column.width) {
                    col.columnWidth = column.width;
                }
                if(selectedIndex !== null) {
                    col.selectedIndex = selectedIndex;
                }
                return col;
            })

            const picker = this.pickerCtrl.create({
                buttons: buttons,
                columns: columns
            });
            picker.present();
        });
    }

}
