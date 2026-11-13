# Diário

Uma entrada por dia, com as suas palavras: o que você tentou, o que decidiu e por quê, o que deu errado
e o que aprendeu. Errar faz parte; o que conta é o que você fez com o erro.

## AAAA-MM-DD

- **Tentei:**
- **Decidi, e por quê:**
- **Deu errado:**
- **Aprendi:**

## 2026-11-08

- **Hoje fiz:**  tive as ideias iniciais do projeto e iniciei a estrutura do projeto, as pastas frontend e backend e o ambiente base
- **Decidi, e por quê:**  decidi fazer o projeto em React + Vite no frontend e python no backend para garantir o melhor equilíbrio entre qualidade visual, desempenho técnico e separação clara de responsabilidades. Estou usando também a API do deepseek, pois é a que possuo no momento. Python é a melhor escolha para manipular dados e consumir a API do deepseek, React + Vite é a melhor escolha criar uma experiência simples, moderna e fácil de usar.

## 2026-11-09

- **Hoje fiz:** comecei a trabalhar no backend do projeto. Fiz uma cópia dos arquivos na pasta de dados para a pasta do backend, fiz um roteiro inicial do feedback, que poderá ser alterado com o avanço do projeto, fiz entidades como Gerente, com busca de anotações por nome, e Vendedor, para calcular métricas como taxa de convertão e ticket médio. Também realizei a integração com a LLM, que no caso é o deepseek.
- **Decidi, e por quê:**  decidi pedir para a ia comentar todo o código que ela criasse, para facilitar o estudo, a compreensão e a anélise do que for gerado, já que ainda não possuo domínio da linguagem.

## 2026-11-11

- **Hoje fiz:** criei 4 endpoints principais em FastAPI (listagem de vendedores, histórico, geração de feedback com IA e consolidado da regional), a gravação local dos roteiros gerados em JSON, os contratos Pydantic para validar os dados e o tratamento padrão de erros. Também comecei a trabalhar no front. Estruturando o cliente central com Axios, os serviços HTTP (com timeout maior para aguardar a IA) e o gerenciamento de estado global com React Context, deixando o app pronto para receber as telas.

- **Aprendi:** Aprendi que um prompt para a IA é melhor quando é pequeno e coeso. Um prompt enorme que manda ler arquivos desnecessários acaba sobrecarregando a IA. Passei a dividir as fatias em frações menores ainda separadas por a, b e c, para obter melhores resultados.

## 2026-11-12

- **Hoje fiz:** trabalhei nas alterações que vaziam mais sentido. Modifiquei a forma que o site havia ficado para se adequar melhor as minhas ideias. Fiz ajustes de UX e implementei chat de anotações. Além disso modifiquei quase que completamente a visão da gestora regional, pois eu queria que fosse similar ao do gerente, podendo fazer feedbacks e anotações, porém não foi isso que foi gerado. Também montei a apresentação ao final do dia.

- **Resolvi mudar:** quando fiz a aba da regional, precisei voltar atrás em alguns pontos, no histórico de commits é possível ver os reverts. Na primeira versão, o sistema funcionava pensando em uma loja só. As anotações da regional eram salvas e gerava o feedback para o gerente sem informar o código da loja nas rotas, assumindo por padrão que tudo era da mesma loja. Porém a gestora regional Patrícia Lemos vai precisar alternar entre várias lojas na barra lateral para avaliar diferentes gerentes. Do jeito antigo, o sistema ficava preso a uma loja só, fugia do padrão que já usado para os vendedores e misturava bibliotecas de teste diferentes (unittest e pytest). Então reorganizei as rotas da API para exigirem o o id da loja na URL e padronizei todos os testes com unittest.

## 2026-11-13

- **Hoje fiz:** Mudei o design do sistema para ficar mais bonito. A estrutura e toda a lógica que já havia sido feita continuou intacta, o que mudou foi apenas o visual.