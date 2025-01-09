from enum import Enum, auto

class ActionType(Enum):
    """Available actions derived from protocol handlers"""
    
    ringshub_Burn = auto()
    
    ringshub_BurnBase = auto()
    
    ringshub_CalculateIssuanceWithCheck = auto()
    
    ringshub_CalculateIssuanceWithCheckBase = auto()
    
    ringshub_GroupMint = auto()
    
    ringshub_GroupMintBase = auto()
    
    ringshub_Migrate = auto()
    
    ringshub_MigrateBase = auto()
    
    ringshub_OperateFlowMatrix = auto()
    
    ringshub_OperateFlowMatrixBase = auto()
    
    ringshub_PersonalMint = auto()
    
    ringshub_PersonalMintBase = auto()
    
    ringshub_RegisterCustomGroup = auto()
    
    ringshub_RegisterCustomGroupBase = auto()
    
    ringshub_RegisterGroup = auto()
    
    ringshub_RegisterGroupBase = auto()
    
    ringshub_RegisterHuman = auto()
    
    ringshub_RegisterHumanBase = auto()
    
    ringshub_RegisterOrganization = auto()
    
    ringshub_RegisterOrganizationBase = auto()
    
    ringshub_SafeBatchTransferFrom = auto()
    
    ringshub_SafeBatchTransferFromBase = auto()
    
    ringshub_SafeTransferFrom = auto()
    
    ringshub_SafeTransferFromBase = auto()
    
    ringshub_SetAdvancedUsageFlag = auto()
    
    ringshub_SetAdvancedUsageFlagBase = auto()
    
    ringshub_SetApprovalForAll = auto()
    
    ringshub_SetApprovalForAllBase = auto()
    
    ringshub_Stop = auto()
    
    ringshub_StopBase = auto()
    
    ringshub_Trust = auto()
    
    ringshub_TrustBase = auto()
    
    ringshub_Wrap = auto()
    
    ringshub_WrapBase = auto()
    
    wxdai_Approve = auto()
    
    wxdai_ApproveBase = auto()
    
    wxdai_Deposit = auto()
    
    wxdai_DepositBase = auto()
    
    wxdai_Transfer = auto()
    
    wxdai_TransferBase = auto()
    
    wxdai_TransferFrom = auto()
    
    wxdai_TransferFromBase = auto()
    
    wxdai_Withdraw = auto()
    
    wxdai_WithdrawBase = auto()
    