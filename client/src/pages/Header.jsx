import React, { useState } from 'react'
import { Wallet } from 'lucide-react'
import Web3 from 'web3'

function Header() {
  const [account, setAccount] = useState(null); 
  const [web3, setWeb3] = useState(null);      

 
  const connectWallet = async () => {
    if (window.ethereum) {
      try {

        await window.ethereum.request({ method: 'eth_requestAccounts' });

        const web3Instance = new Web3(window.ethereum);
        setWeb3(web3Instance);

        const accounts = await web3Instance.eth.getAccounts();
        setAccount(accounts[0]);  
        console.log('Connected account:', accounts[0]);
      } catch (error) {
        console.error("Failed to connect wallet", error);
      }
    } else {
      console.log("MetaMask is not installed. Please install it to use this feature.");
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <header className="sticky top-0 z-50 bg-black/30 backdrop-blur-lg border-b border-gray-500/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl flex gap-3 font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            <img className='w-8 h-6' src="/Logo.png" alt="Logo" />
            <img className='w-full h-6' src="/LogoName.png" alt="LogoName" />
          </div>
          <button
            onClick={connectWallet}
            className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full hover:from-blue-600 hover:to-purple-700 transition duration-300 flex items-center space-x-2 shadow-lg hover:shadow-blue-500/25"
          >
            <Wallet className="h-5 w-5" />
            <span>{account ? `Connected: ${account.slice(0, 6)}...${account.slice(-4)}` : "Connect Wallet"}</span>
          </button>
        </div>
      </header>
    </div>
  );
}

export default Header;
