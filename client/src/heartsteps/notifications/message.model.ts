import { MessageReceiptService } from "./message-receipt.service";


export class Message {
    public id: string;
    public type: string;

    public title: string;
    public body: string;

    public survey: any;

    public context: any = {};

    constructor(
        private messageRecieptService: MessageReceiptService
    ) {}

    public received():Promise<boolean> {
        return this.messageRecieptService.received(this.id);
    }

    public displayed(): Promise<boolean> {
        return this.messageRecieptService.displayed(this.id);
    }

    public opened():Promise<boolean> {
        return this.messageRecieptService.opened(this.id);
    }

    public engaged():Promise<boolean> {
        return this.messageRecieptService.engaged(this.id);
    }

}

