import { Component } from "@angular/core";
import { PageComponent } from "./page.component";

@Component({
    selector: 'app-modal',
    templateUrl: './modal.component.html'
})
export class ModalComponent extends PageComponent {

    dismissText: string = "Cancel";

}
