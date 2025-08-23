import { useState } from 'react'
import './CadastroUsuario.css'

const CadastroUsuario = () => {
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    imagem: null
  })
  const [loading, setLoading] = useState(false)
  const [mensagem, setMensagem] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const data = new FormData()
    data.append('nome', formData.nome)
    data.append('email', formData.email)
    data.append('imagem', formData.imagem)

    try {
      const response = await fetch('http://EC2_IP:5000/usuarios', {
        method: 'POST',
        body: data
      })

      if (response.ok) {
        setMensagem('Usuário cadastrado com sucesso!')
        setFormData({ nome: '', email: '', imagem: null })
      } else {
        setMensagem('Erro ao cadastrar usuário')
      }
    // eslint-disable-next-line no-unused-vars
    } catch (error) {
      setMensagem('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cadastro-container">
      <h2>Cadastrar Usuário</h2>
      <form onSubmit={handleSubmit} className="cadastro-form">
        <input
          type="text"
          placeholder="Nome"
          value={formData.nome}
          onChange={(e) => setFormData({...formData, nome: e.target.value})}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFormData({...formData, imagem: e.target.files[0]})}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Cadastrando...' : 'Cadastrar'}
        </button>
      </form>
      {mensagem && <p className="mensagem">{mensagem}</p>}
    </div>
  )
}

export default CadastroUsuario