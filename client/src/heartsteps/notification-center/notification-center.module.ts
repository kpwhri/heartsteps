import { NgModule } from "@angular/core";

import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { NotificationCenterService } from "./notification-center.service";

@NgModule({
    imports: [InfrastructureModule],
    providers: [NotificationCenterService],
})
export class NotificationCenterModule {}
