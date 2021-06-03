import { NgModule } from "@angular/core";
import { HeartstepsComponentsModule } from "@infrastructure/components/components.module";
import { PageComponent } from "@infrastructure/components/page.component";
import { IonicPageModule } from "ionic-angular";
import { NotificationCenterPage } from "./notification-center";

@NgModule({
    declarations: [NotificationCenterPage],
    imports: [
        // TODO: figure out why HeartstepsComponentsModule import doesn't let me use <app-page>
        HeartstepsComponentsModule,
        // TODO: remove PageComponent
        // should already be imported in HeartstepsComponentsModule
        PageComponent,
        IonicPageModule.forChild(NotificationCenterPage),
    ],
    exports: [NotificationCenterPage],
})
export class NotificationCenterPageModule {}
