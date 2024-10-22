
import { ethers } from 'ethers';
import contractABI from './BatteryPassportABI.json';

const contractAddress = "YOUR_SMART_CONTRACT_ADDRESS";

export const getContract = async () => {
  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const signer = provider.getSigner();
  const contract = new ethers.Contract(contractAddress, contractABI, signer);
  return contract;
};

export const connectWallet = async () => {
  if (window.ethereum) {
    await window.ethereum.request({ method: 'eth_requestAccounts' });
    return getContract();
  } else {
    alert('Please install MetaMask to use this feature');
  }
};
