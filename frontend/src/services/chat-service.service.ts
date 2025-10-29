import { Injectable } from '@angular/core';
import axios from 'axios';

@Injectable({ providedIn: 'root' })
export class ChatServiceService {
  baseUrl = 'http://127.0.0.1:5000';

  async askJuridique(question: string) {
    const res = await axios.post(`${this.baseUrl}/ask`, { question });
    return res.data;
  }

  async askWithConversation(question: string, conversation_id?: string) {
    const payload: any = { question };
    if (conversation_id) payload.conversation_id = conversation_id;
    const res = await axios.post(`${this.baseUrl}/ask`, payload);
    return res.data;
  }

  async createConversation(title?: string) {
    const res = await axios.post(`${this.baseUrl}/conversations`, { title });
    return res.data;
  }

  async addMessage(conversation_id: string, role: string, text: string, timestamp?: string) {
    const res = await axios.post(`${this.baseUrl}/conversations/${conversation_id}/messages`, { role, text, timestamp });
    return res.data;
  }

  async listConversations() {
    const res = await axios.get(`${this.baseUrl}/conversations`);
    return res.data;
  }

  async getConversation(conversation_id: string) {
    const res = await axios.get(`${this.baseUrl}/conversations/${conversation_id}`);
    return res.data;
  }
}
