import { Injectable } from '@angular/core';
import axios from 'axios';

@Injectable({ providedIn: 'root' })
export class ChatServiceService {
  baseUrl = 'http://127.0.0.1:5000';

  async askJuridique(question: string) {
    const res = await axios.post(`${this.baseUrl}/ask`, { question });
    return res.data;
  }
}
