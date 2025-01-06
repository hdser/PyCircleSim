from enum import Enum, auto

class ActionType(Enum):
    """Available actions derived from protocol handlers"""
    
    balancerv3vault_AddLiquidity = auto()
    
    balancerv3vault_Erc4626BufferWrapOrUnwrap = auto()
    
    balancerv3vault_RemoveLiquidity = auto()
    
    balancerv3vault_SendTo = auto()
    
    balancerv3vault_Settle = auto()
    
    balancerv3vault_Swap = auto()
    
    balancerv3vault_Transfer = auto()
    
    balancerv3vault_TransferFrom = auto()
    
    balancerv3vault_Unlock = auto()
    
    fjordlbpproxyv6_AddFundTokenOptions = auto()
    
    fjordlbpproxyv6_CreateLBP = auto()
    
    fjordlbpproxyv6_CreateWeightedPoolForLBP = auto()
    
    fjordlbpproxyv6_ExitPool = auto()
    
    fjordlbpproxyv6_RenounceOwnership = auto()
    
    fjordlbpproxyv6_SetSwapEnabled = auto()
    
    fjordlbpproxyv6_Skim = auto()
    
    fjordlbpproxyv6_TransferOwnership = auto()
    
    fjordlbpproxyv6_TransferPoolOwnership = auto()
    
    fjordlbpproxyv6_UpdateRecipients = auto()
    
    ringshub_Burn = auto()
    
    ringshub_CalculateIssuanceWithCheck = auto()
    
    ringshub_GroupMint = auto()
    
    ringshub_Migrate = auto()
    
    ringshub_OperateFlowMatrix = auto()
    
    ringshub_PersonalMint = auto()
    
    ringshub_RegisterCustomGroup = auto()
    
    ringshub_RegisterGroup = auto()
    
    ringshub_RegisterHuman = auto()
    
    ringshub_RegisterOrganization = auto()
    
    ringshub_SafeBatchTransferFrom = auto()
    
    ringshub_SafeTransferFrom = auto()
    
    ringshub_SetAdvancedUsageFlag = auto()
    
    ringshub_SetApprovalForAll = auto()
    
    ringshub_Stop = auto()
    
    ringshub_Trust = auto()
    
    ringshub_Wrap = auto()
    