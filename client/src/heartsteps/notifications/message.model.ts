import { MessageReceiptService } from "./message-receipt.service";

export class Message {
    public id: string;
    public type: string;
    public created: any;

    public title: string;
    public body: string;

    public sent: any;
    public received: any;
    public opened: any;
    public engaged: any;

    public survey: any;

    public context: any = {};

    constructor(private messageRecieptService: MessageReceiptService) {}

    public toggleReceived(): Promise<boolean> {
        return this.messageRecieptService.received(this.id);
    }

    public toggleDisplayed(): Promise<boolean> {
        return this.messageRecieptService.displayed(this.id);
    }

    public toggleOpened(): Promise<boolean> {
        return this.messageRecieptService.opened(this.id);
    }

    public toggleEngaged(): Promise<boolean> {
        return this.messageRecieptService.engaged(this.id);
    }
}
