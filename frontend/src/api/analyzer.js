import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
    timeout: 35000,
})

export const analyzeText = async (text, inputType = 'TEXT') => {
    const { data } = await api.post('/analyze', { text, inputType })
    return data
}

export const getHistory = async () => {
    const { data } = await api.get('/history')
    return data
}